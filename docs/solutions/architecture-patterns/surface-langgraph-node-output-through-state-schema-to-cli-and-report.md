---
title: Surfacing a New LangGraph Node Output Through State Schema, CLI Accumulation, and Report Renderer
date: 2026-08-17
category: architecture-patterns
module: taxonomy_generator
problem_type: architecture_pattern
component: service_layer
severity: medium
applies_when:
  - "Adding a new node-level output (a value a LangGraph node computes and returns) that must become visible in this CLI's final JSON output and/or its generated report"
  - "The graph is built with StateGraph(State, input_schema=InputState, output_schema=OutputState, ...) so a node's returned dict key is silently dropped unless it is also a declared field on State/OutputState"
  - "main.py accumulates astream(..., stream_mode=\"updates\") output into local variables by hand rather than reading the graph's final state object directly"
tags: [langgraph, state-schema, output-schema, dimension-selector, report-renderer, taxonomy-generator, cli-accumulation, dropped-dimensions]
---

# Surfacing a New LangGraph Node Output Through State Schema, CLI Accumulation, and Report Renderer

From the commit "feat(report): ground narrative in the use case and surface discarded dimensions" on branch `feat/grounded-theory-report` (local-only as of this writing, not yet merged — cite the PR once opened rather than the commit SHA, which rebase/squash can rewrite). Files touched: `main.py`, `src/taxonomy_generator/nodes/dimension_selector.py`, `src/taxonomy_generator/prompts/narrative_summary.md`, `src/taxonomy_generator/report_renderer.py`, `src/taxonomy_generator/state.py`.

## Context

This session added two independent pieces of work to the grounded-theory report feature:

1. **Narrative use-case grounding (prompt-only).** `generate_narrative_summary` (`src/taxonomy_generator/report_renderer.py:259-311`) already builds its prompt with `NARRATIVE_SUMMARY_PROMPT.partial(use_case=configuration.use_case)` (`report_renderer.py:290-292`), and the prompt template (`src/taxonomy_generator/prompts/narrative_summary.md:7`) already surfaces `{use_case}` under a "## Context" heading. The gap was that the prompt's "## Guidelines" section never told the model to *do* anything with that use case — it was background context the model was free to ignore. The fix added one guideline bullet (`narrative_summary.md:24`), reproduced under Examples below. No code changed for this half — it's a pure prompt-instruction fix, the same mechanism used for a related, earlier bug in this same feature (see Related, below).

2. **Discarded Dimensions section (schema + code across 5 files).** The "selective coding" step, `select_dimensions` in `src/taxonomy_generator/nodes/dimension_selector.py`, has always dropped taxonomy dimensions judged irrelevant to the configured use case. Before this change, the *rationale* for each drop only reached `State.status` as prose (`dimension_selector.py:78-81`, an `Annotated[List[str], operator.add]` log accumulator on `State`, `state.py:82`) — never surfaced in any JSON output file or in the `--report` markdown. The only way to see why a dimension was dropped was to read debug logs. This is the general situation the reusable guidance below addresses: **how to take a value a node already computes and get it all the way through this pipeline's schema-gated graph, into `main.py`'s manually-accumulated CLI state, and into both output artifacts (`*_taxonomy_*.json` and the `--report` markdown).**

## Guidance

This codebase's data flow from "a node computes a value" to "a user can see it" crosses four distinct boundaries, and **all four must be touched** — updating only the schema, or only the node, silently produces a value that never reaches any file. The reusable recipe, illustrated with the actual `dropped_dimensions` field added by this change:

**1. Declare the field on both `OutputState` and `State` in `src/taxonomy_generator/state.py`.**

The graph is built as `StateGraph(State, input_schema=InputState, output_schema=OutputState, context_schema=Configuration)` (`src/taxonomy_generator/graph.py:26`). LangGraph only lets a node's returned dict key flow through the graph, and only lets it appear on the final accumulated result, if that key corresponds to a field declared on the schema class(es) passed to `StateGraph` — here, `State` (the internal working schema every node reads/writes) and `OutputState` (what the compiled graph exposes as its output shape). A key a node returns that isn't declared on `State` is simply dropped by the graph. `state.py:68` (`OutputState`) and `state.py:93-95` (`State`) both needed the new field:

```python
# OutputState (state.py:68)
dropped_dimensions: List[Dict] = field(default_factory=list)

# State (state.py:93-95)
# Dimensions dimension-selection excluded from selected_clusters, kept
# inspectable with a rationale rather than only logged to `status`.
dropped_dimensions: List[Dict] = field(default_factory=list)
```

**2. Return the value from the producing node.** `select_dimensions` (`dimension_selector.py:31-88`) now returns it flat in its result dict:

```python
# dimension_selector.py:83-88
return {
    "selected_clusters": [selected],
    "dropped_dimensions": dropped,
    "explanations": [result.rationale],
    "status": status,
}
```

**Type-shape gotcha, worth flagging explicitly:** in that same return statement, the sibling field `selected_clusters` is wrapped in an *extra* list — `[selected]`, not `selected` — because `State.selected_clusters` is typed `List[List[Dict]]` (one list per selection round; `state.py:92`). `dropped_dimensions`, by contrast, is typed `List[Dict]` directly (`state.py:68`, `state.py:95`) and so is returned flat (`dropped`, not `[dropped]`). Two fields written in the same return statement by the same node have different nesting depth. When adding a similar field later, check the declared type on `State`/`OutputState` for the *specific* field being added — don't pattern-match against a neighboring field's wrapping.

**3. Update `main.py`'s manual per-node accumulation — in three separate places.** `main.py`'s `run()` does not rely solely on the graph's final accumulated state; it streams `graph.astream(invoke_input, config=run_config, stream_mode="updates")` (`main.py:751`) and manually re-accumulates each node's incremental output dict into local Python variables as it iterates. A schema change in step 1 is necessary but **not sufficient** — the same field name must independently be wired into three spots inside `run()`:

- (a) Local variable initialization before the stream loop: `dropped_dimensions: list = []` (`main.py:736`)
- (b) Accumulation inside the loop, keyed off the node's output dict: `if "dropped_dimensions" in node_output: dropped_dimensions = node_output["dropped_dimensions"]` (`main.py:784-785`)
- (c) Conditional inclusion when assembling the final `taxonomy_data` dict for JSON serialization: `if dropped_dimensions: taxonomy_data["dropped_dimensions"] = dropped_dimensions` (`main.py:876-877`)

Forgetting any one of (a)/(b)/(c) means the field exists on the graph's `OutputState` and even shows up in the generic `result.update(node_output)` catch-all (`main.py:796`) yet never reaches the saved JSON file, because the JSON-writing code path reads from the named local variable, not from `result`.

A second helper, `_dropped_dimensions_for_view` (`main.py:529-551`), resolves the field for the `--report`/auto-report rendering path — modeled on the pre-existing `_explanation_for_view` (`main.py:499-526`). Both share the signature shape `(data: Any, iteration_arg: Optional[int]) -> ...` and the purpose of resolving a value tied to *one specific* view of a saved taxonomy JSON, but they diverge on purpose:

```python
# main.py:499-526 — falls back to the latest iteration's explanation
# when no per-view explanation exists (still returns *something*)
def _explanation_for_view(data: Any, iteration_arg: Optional[int]) -> str:
    ...
    if not isinstance(data, dict):
        return ""
    iterations = data.get("iterations") or []
    if iteration_arg is not None:
        if 1 <= iteration_arg <= len(iterations):
            return iterations[iteration_arg - 1].get("explanation") or ""
        return ""
    if iterations:
        return iterations[-1].get("explanation") or ""
    return ""

# main.py:529-551 — returns nothing at all whenever --iteration is given
def _dropped_dimensions_for_view(
    data: Any, iteration_arg: Optional[int]
) -> Tuple[List[Any], List[Any]]:
    """Resolve discarded-dimension data for the rendered view, when applicable.

    Discarded-dimension rationale is recorded once, for the single
    dimension-selection step that produced ``selected_clusters`` from the
    taxonomy's final iteration — it only applies when that is the view
    actually being rendered (no explicit ``--iteration`` override) and the
    file recorded it (older files predating this feature have neither key).
    """
    if iteration_arg is not None or not isinstance(data, dict):
        return [], []
    dropped = data.get("dropped_dimensions") or []
    if not dropped:
        return [], []
    iterations = data.get("iterations") or []
    all_clusters = iterations[-1].get("clusters") or [] if iterations else []
    return dropped, all_clusters
```

The `iteration_arg is not None` short-circuit is deliberate: dropped-dimension rationale is intrinsically tied to the one-time `select_dimensions` step that ran once against the final/selected taxonomy view. Rendering `--report --iteration 3` shows an arbitrary earlier iteration that predates or is unrelated to that selection step, so showing discard rationale alongside it would misattribute the rationale — hence returning `([], [])` rather than reusing the latest iteration's data the way `_explanation_for_view` does. `main.py` calls this helper from both the standalone `--report` path (`main.py:624`, `_run_report`) and the auto-report path inside `run()`'s `--output` handling (`main.py:984-986`).

**4. Thread the value through `report_renderer.py`'s rendering functions.** A new function, `render_discarded_dimensions(dropped, all_clusters) -> str` (`report_renderer.py:209-246`), renders the markdown section. Because a dropped dimension is by definition absent from the selected/rendered cluster list passed to the rest of the report, its display `name` must be looked up from a *separate*, full pre-selection cluster list:

```python
# report_renderer.py:229
clusters_by_id = {_cluster_id(c): c for c in all_clusters}
```

This is the same `{_cluster_id(c): c for c in ...}` lookup-table idiom already used in `render_catalog` (`report_renderer.py:152`) for resolving relation targets — reused rather than reinvented. The section renders in numeric dimension-id order via the pre-existing `_in_id_order` helper (`report_renderer.py:68-76`, itself added in an earlier commit on this branch for an unrelated dimension-catalog ordering fix, not new in this change).

Two call chains both needed extending with the new data, in lockstep:

```python
# report_renderer.py:314-319 — assemble_report
def assemble_report(
    clusters: List[Cluster],
    narrative_summary_or_none: str | None,
    dropped_dimensions: List[Cluster] | None = None,
    all_clusters_for_dropped: List[Cluster] | None = None,
) -> str: ...

# report_renderer.py:373-380 — generate_and_write_report (the shared entry
# point both --report and the auto-report path call)
async def generate_and_write_report(
    clusters: List[Cluster],
    explanation: str,
    configuration: Configuration,
    out_path: Path,
    dropped_dimensions: List[Cluster] | None = None,
    all_clusters_for_dropped: List[Cluster] | None = None,
) -> str | None: ...
```

Both new parameters are optional trailing params (default `None`), so existing callers don't break. `assemble_report` places the rendered section last, only when non-empty:

```python
# report_renderer.py:365-368
discarded = render_discarded_dimensions(dropped_dimensions or [], all_clusters_for_dropped or [])
if discarded:
    lines.append("")
    lines.append(discarded)
```

**Type-annotation convention in this file:** `report_renderer.py` has `from __future__ import annotations` (`report_renderer.py:17`) and consistently spells optional types as `X | None` (e.g. `str | None` at `report_renderer.py:263`, `List[Cluster] | None = None` at `report_renderer.py:317-318`), not `Optional[X]`. `ruff`'s `UP045` rule flags `Optional[X]` specifically in files with this import present — use `X | None` when adding new optional parameters here.

## Why This Matters

- **LangGraph's schema-gated field flow is a silent trap.** Adding a key to a node's returned dict with no corresponding field on `State`/`OutputState` doesn't raise an error — the graph just never surfaces it. There's no runtime signal that the field was dropped; it has to be caught by knowing to check the `StateGraph(...)` construction line (`graph.py:26`) against the schema classes.
- **`main.py`'s manual `astream(..., stream_mode="updates")` accumulation means the schema change alone is never sufficient here.** Because `run()` builds its own local variables from each node's incremental output rather than trusting a single final-state object, a field can be fully correct at the graph layer (visible in `OutputState`, returned by the node) and still never reach a saved JSON file if `main.py` wasn't independently updated in all three of its accumulation points. This is easy to miss because `result.update(node_output)` (`main.py:796`) *does* silently capture every field into a generic `result` dict — but that dict is not what `taxonomy_data` (the thing actually written to disk) is built from, so its presence there gives false confidence that "the data is captured."
- **The flat-vs-nested-list type mismatch between `selected_clusters` (`[selected]`) and `dropped_dimensions` (`dropped`, unwrapped) in the same return statement (`dimension_selector.py:84-85`) is an easy copy-paste trap.** A future field added by copying the `selected_clusters` line's wrapping without checking its own declared type on `State` would silently produce a mis-shaped value, likely only surfacing as a downstream `.get()`/iteration bug far from the point of the mistake.
- **The `_dropped_dimensions_for_view` / `_explanation_for_view` divergence on `--iteration` handling is a case where copying a "same-shape" helper without checking its returned-value semantics would be wrong.** Both helpers resolve view-scoped data from a saved taxonomy JSON and take the same `(data, iteration_arg)` signature, but they diverge on purpose. A naive copy-paste of one helper's fallback behavior onto the other would produce semantically wrong output (discard rationale shown against an iteration the selection step never touched) without any test or lint catching it, since this repo has no automated test suite.

## When to Apply

- Adding any new field that a node in this pipeline (`src/taxonomy_generator/nodes/*.py`) produces and that should be exposed in either of this CLI's user-facing output surfaces: the saved `*_taxonomy_*.json` (or sibling `*_documents_*.json`/`*_messages_*.json`/`*_clusters_*.json`) files written under `--output`, or the `--report` / auto-generated markdown report.
- Does **not** apply to fields that only need to be visible in `State.status` prose logging, or fields already covered by an existing accumulation path (e.g. anything already flowing through `clusters`/`explanations`/`documents`/`messages`, which `main.py` already accumulates and serializes).

The four-step checklist:

1. Declare the field on both `State` and `OutputState` in `src/taxonomy_generator/state.py`, matching the exact list/dict nesting the field actually needs (verify against how the value is constructed in the producing node — don't copy a neighboring field's shape).
2. Return the field from the producing node's return dict, using the shape declared in step 1.
3. In `main.py`'s `run()`, add all three of: local variable init, an `if "<field>" in node_output:` accumulation line inside the `astream` loop, and a conditional line building `taxonomy_data` (or the relevant output dict) before it's serialized to JSON.
4. If the field should also appear in the `--report` markdown, add a resolution helper in `main.py` (model it on `_explanation_for_view`/`_dropped_dimensions_for_view` — but decide independently, not by copying, what should happen under `--iteration N`), a rendering function in `report_renderer.py`, and thread it through as new optional trailing parameters on both `assemble_report` and `generate_and_write_report`, calling the new render function from `assemble_report` and appending its output only when non-empty.

## Examples

**Schema (`src/taxonomy_generator/state.py`) — before/after, `OutputState`:**

```python
# Before
@dataclass
class OutputState:
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)
    clusters: Annotated[List[List[Dict]], operator.add] = field(default_factory=list)
    explanations: Annotated[List[str], operator.add] = field(default_factory=list)
    documents: List[Doc] = field(default_factory=list)
    selected_clusters: List[List[Dict]] = field(default_factory=list)

# After (state.py:68)
    selected_clusters: List[List[Dict]] = field(default_factory=list)
    dropped_dimensions: List[Dict] = field(default_factory=list)
```

**`main.py` — the three accumulation points, before/after:**

```python
# Before (run(), local var block)
clusters: list = []
selected_clusters: list = []
saturation_history: list = []
...
# After (main.py:734-737)
clusters: list = []
selected_clusters: list = []
dropped_dimensions: list = []
saturation_history: list = []
```

```python
# Before (astream loop body)
if "selected_clusters" in node_output:
    selected_clusters = node_output["selected_clusters"]
# After (main.py:782-785)
if "selected_clusters" in node_output:
    selected_clusters = node_output["selected_clusters"]
if "dropped_dimensions" in node_output:
    dropped_dimensions = node_output["dropped_dimensions"]
```

```python
# Before (taxonomy_data assembly)
if selected_clusters:
    taxonomy_data["selected_clusters"] = selected_clusters[-1]
# After (main.py:874-877)
if selected_clusters:
    taxonomy_data["selected_clusters"] = selected_clusters[-1]
if dropped_dimensions:
    taxonomy_data["dropped_dimensions"] = dropped_dimensions
```

**`report_renderer.py` — new render function and signature threading:**

```python
# report_renderer.py:209-246 (new function)
def render_discarded_dimensions(dropped: List[Cluster], all_clusters: List[Cluster]) -> str:
    if not dropped:
        return ""
    clusters_by_id = {_cluster_id(c): c for c in all_clusters}
    lines = ["## Discarded Dimensions", "", "Dimensions considered during taxonomy "
             "generation but excluded from this view during dimension selection, "
             "judged not relevant to the stated use case:", ""]
    for item in _in_id_order(dropped):
        did = _cluster_id(item)
        source = clusters_by_id.get(did)
        name = (source.get("name") if source else None) or "Unnamed"
        rationale = item.get("rationale") or "No rationale recorded."
        lines.append(f"- **{did}. {name}** — {rationale}")
    return "\n".join(lines)
```

**Prompt guideline addition (`src/taxonomy_generator/prompts/narrative_summary.md:24`):**

```
- **Ground the summary in the use case.** Check whether the taxonomy explanation
  already makes clear what question or use case this taxonomy serves. If it does,
  no change needed. If it doesn't — or only implies it — open with a brief sentence
  stating the use case plainly, so a reader with no prior context knows why these
  particular dimensions were chosen before reading further.
```

## Verification Performed

- `mypy --strict` and `ruff check` were run against all 5 touched files; both confirmed no new findings beyond this repo's pre-existing baseline lint/type debt. This repo has no automated test suite — `mypy`+`ruff` (wired as `make lint`) are the only automated gates.
- A full end-to-end pipeline run (`python main.py --corpus examples/campus-bike/campus_bike_architecture_decisions.json --config examples/campus-bike/campus_bike_config.yaml --output examples/campus-bike/`) exercised the use-case-grounding narrative change against a real LLM call. That run selected all 7 dimensions (0 dropped), so it did not exercise the Discarded Dimensions rendering path.
- The Discarded Dimensions section was verified separately with a synthetic taxonomy JSON: that real run's output JSON was copied and hand-edited to shrink `selected_clusters` to 5 entries and add a `dropped_dimensions` array with 2 synthetic `{id, rationale}` entries, then rendered via `python main.py --report <synthetic.json> --output <dir>` (the deterministic, non-LLM diagram/catalog/discarded rendering path — the narrative section alone still calls the LLM). This confirmed correct numeric-id ordering, correct name resolution via the full-cluster lookup, and — importantly — that the narrative summary stayed scoped to only the 5 selected dimensions with no leakage of the 2 dropped dimensions' content. This last check is a re-verification of the invariant fixed by the *earlier*, distinct bug documented below (narrative text leaking references to dimensions outside the rendered view) — not a re-fix of that bug, but confirmation the new discarded-dimensions data path doesn't reopen it.

## Related

- `docs/solutions/logic-errors/narrative-summary-includes-unscoped-explanation-text.md` — a different, earlier bug in the same narrative-summary code path (a free-text `explanation` field leaking references to dimensions excluded from the rendered view). Related area, same mechanism (prompt-instruction-only fix, no post-hoc validation), but a distinct problem, root cause, and prevention rule — not a duplicate of this doc.
- `docs/plans/2026-08-16-2115-feat-grounded-theory-report-plan.md` — the originating unified plan for the broader Grounded Theory Report feature this commit builds on.
