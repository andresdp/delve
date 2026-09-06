---
title: Taxonomy Evaluation Suite with Scoreboard and Consistency Comparison
date: 2026-08-21
last_updated: 2026-09-05
category: architecture-patterns
module: taxonomy_generator
problem_type: architecture_pattern
component: service_layer
severity: medium
applies_when:
  - "You need to evaluate the quality of a generated taxonomy without rerunning the pipeline"
  - "You want to compare multiple saved taxonomies from the same corpus for run-to-run consistency"
  - "You want in-graph, observe-only evaluation that never routes or fails the pipeline"
  - "You are verifying that a plan's described graph wiring was actually completed, not just designed and partially built"
tags: [taxonomy-evaluation, scoreboard, consistency-comparison, deepeval, grounded-theory-report, evaluation-node, standalone-cli, dead-code, graph-wiring-verification]
---

# Taxonomy Evaluation Suite with Scoreboard and Consistency Comparison

## Context

Delve's taxonomy pipeline historically had strong *generation* and *reporting* support but no way to measure how good a produced taxonomy actually was or to compare taxonomies across runs. The quality criteria (orthogonality, clarity, completeness, use-case alignment, no catch-alls, axis-vs-value, coverage) only lived as prose in the review prompt, consulted once during a run and then lost. There was also no surface to compare saved taxonomies from repeated runs on the same corpus.

The **Taxonomy Evaluation Suite** closes this gap by:

- Turning the existing review criteria into **deepeval GEval metrics** (`evaluation/metrics.py`, `evaluation/runner.py`).
- Providing an **observe-only in-graph evaluation node** that scores the effective taxonomy view during a run without affecting routing (`nodes/taxonomy_evaluator.py`, `state.py`, `graph.py`).
- Adding a **standalone `--evaluate` CLI mode** that can score one saved taxonomy or compare several for consistency (`main.py:_run_evaluate`).
- Surfacing results as a **rich scoreboard panel**, a saved **JSON artifact**, and a **`## Evaluation` section** in the grounded-theory report (`main.py:_display_scoreboard`, `report_renderer.py:render_evaluation`, `report_renderer.py:assemble_report`).

This doc captures the architecture pattern that ties those pieces together so future evaluation work (new criteria, different judge models, alternative comparison strategies) can reuse the same skeleton.

## Guidance

The evaluation suite glues three concerns together:

1. **Turn review criteria into reusable judge metrics (deepeval GEval).**
2. **Run those metrics in two modes** — in-graph (observe-only) and standalone.
3. **Surface results consistently across terminal, JSON, and report.**

The pattern below assumes you keep deepeval as an embedded metric library, *not* as the project's test harness.

### 1. Define criteria and GEval metrics

`src/taxonomy_generator/evaluation/metrics.py` owns the mapping from the review prompt's criteria table to concrete `GEval` instances:

- `Criterion` dataclass describes each criterion:
  - `name`: display name (e.g. "Orthogonality").
  - `criteria`: everyday-language judging instructions adapted from `prompts/taxonomy_review.md`.
  - `needs_documents`: whether this criterion requires document text.
- `STRUCTURAL_CRITERIA` holds six criteria that only need the taxonomy view.
- `COVERAGE_CRITERION` captures the data-grounded coverage check and sets `needs_documents=True`.
- `build_metrics(model, threshold, include_coverage) -> List[GEval]`:
  - Accepts a bare OpenAI model name or `None` and a display-only `threshold`.
  - Decides whether to append `COVERAGE_CRITERION` based on `include_coverage`.
  - Constructs one `GEval` per `Criterion`:

    ```python
    metric = GEval(
        name=criterion.name,
        criteria=criterion.criteria,
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=threshold,
        model=model,
        async_mode=True,
    )
    metric._criterion = criterion  # attached for runner use
    ```

**Pattern:** keep criteria text close to the original review plan, but expressed in everyday language a judge model can follow. Each metric only sees `(input, actual_output)` — no hidden reference fields.

### 2. Implement a scoreboard runner with graceful degradation

`src/taxonomy_generator/evaluation/runner.py` turns a taxonomy view and optional document sample into a plain scoreboard dict.

Key steps in `run_scoreboard(clusters, documents, configuration)`:

1. **Resolve judge model and threshold**

   ```python
   judge_model = resolve_judge_model(
       configuration.evaluation_judge_model or configuration.model
   )
   threshold = configuration.evaluation_threshold
   ```

   `resolve_judge_model` (in `evaluation/judge.py`) strips the `openai/` prefix when present and returns a bare model name for deepeval's OpenAI integration, or `None` to let GEval choose its default. Non-OpenAI providers raise a clear `ValueError`, documented as the future hook for a `DeepEvalBaseLLM` adapter.

2. **Serialize the taxonomy view once**

   ```python
   taxonomy_json = format_taxonomy(clusters)
   ```

   This reuses the existing view-serialization logic rather than inventing a separate prompt format.

3. **Decide whether coverage is active**

   ```python
   docs = list(documents or [])
   include_coverage = bool(docs)
   metrics = build_metrics(judge_model, threshold, include_coverage)
   ```

4. **Build structural and coverage test cases**

   ```python
   structural_case = LLMTestCase(
       input=configuration.use_case,
       actual_output=taxonomy_json,
   )
   coverage_case = (
       LLMTestCase(
           input="\n\n".join(
               _doc_content(d)
               for d in docs[: configuration.evaluation_max_documents]
           ),
           actual_output=taxonomy_json,
       )
       if include_coverage
       else None
   )
   ```

5. **Measure each metric and build criteria rows**

   ```python
   criteria_rows: List[Dict] = []
   scores: List[float] = []
   for metric in metrics:
       criterion = metric._criterion  # attached in build_metrics
       case = coverage_case if criterion.needs_documents else structural_case
       await metric.a_measure(case, _show_indicator=False)
       row = {
           "name": criterion.name,
           "threshold": threshold,
           "evaluated": True,
       }
       if metric.score is not None:
           row["score"] = float(metric.score)
           row["passed"] = bool(metric.score >= threshold)
           scores.append(float(metric.score))
       else:
           row["score"] = None
           row["passed"] = None
       row["reason"] = metric.reason or ""
       criteria_rows.append(row)
   ```

6. **Ensure coverage is visibly "not evaluated" when documents are absent**

   ```python
   if not include_coverage:
       criteria_rows.append(
           {
               "name": COVERAGE_CRITERION.name,
               "threshold": threshold,
               "score": None,
               "passed": None,
               "reason": "",
               "evaluated": False,
           }
       )
   ```

7. **Compute overall and return a flat dict**

   ```python
   overall = sum(scores) / len(scores) if scores else None
   return {
       "criteria": criteria_rows,
       "overall": overall,
       "model": configuration.evaluation_judge_model or configuration.model,
       "unavailable": False,
   }
   ```

8. **Degrade on any exception instead of failing the run**

   The entire function is wrapped in a `try/except Exception` block. On failure it logs a warning and returns:

   ```python
   return {
       "criteria": [],
       "overall": None,
       "model": configuration.evaluation_judge_model or configuration.model,
       "unavailable": True,
       "error": str(exc),
   }
   ```

**Pattern:** the scoreboard runner *never* raises; callers see a self-describing unavailable scoreboard instead of an exception.

### 3. Compare multiple taxonomies for consistency

`src/taxonomy_generator/evaluation/consistency.py` provides `compare_taxonomies(taxonomies, configuration)`, which aligns dimensions across saved taxonomy views and reports recurring vs one-off dimensions plus an agreement score.

Key pieces:

- `_dimension_text(cluster)` serializes one dimension as `name + description + value labels`.
- `_dimension_label(cluster, file_index, dim_index)` builds a stable identity record per dimension occurrence.
- `_cross_distances(vectors)` computes a full pairwise Euclidean distance matrix for L2-normalized embedding vectors.

`compare_taxonomies`:

1. Flattens each taxonomy's clusters into `dims` and `texts`.
2. Uses `load_embeddings_model(configuration.embedding)` and `l2_normalize` to get numeric vectors, then `_cross_distances` to compute distances.
3. Builds alignment edges in two tiers:
   - Deterministic: distances `<= threshold` form edges directly.
   - Borderline band: distances between `threshold` and `threshold + band` route to a single judge call via `_adjudicate_same_dimension`, which uses OpenAI's `AsyncOpenAI` client with a short yes/no question.
4. Falls back to exact-name matching if embedding loading fails, with a logged warning and a `fallback: "exact-name"` marker in the result.
5. Uses `connected_components` from `utils.py` to group aligned dimensions, then derives:
   - `recurring`: groups touching more than one file.
   - `one_offs`: dimensions that appear in only one file.
   - `agreement`: `aligned / max_count` across files, rounded to 4 decimals.

Returned shape:

```python
{
    "files": len(taxonomies),
    "agreement": float | None,
    "recurring": [...],
    "one_offs": [...],
    "adjudicated_pairs": adjudicated,
    "fallback": fallback,  # e.g. "exact-name" or None
    "unavailable": False,
}
```

On total failure, it degrades to `{"unavailable": True, "error": ...}` instead of raising.

### 4. Add an observe-only in-graph evaluation node

`src/taxonomy_generator/state.py` and `src/taxonomy_generator/nodes/taxonomy_evaluator.py` carry the in-graph wiring.

State additions in `state.py`:

- `OutputState.evaluation: Optional[Dict]` and `State.evaluation: Optional[Dict]` store the latest scoreboard with replace semantics. This follows the same "declare on both State and OutputState" pattern as other surfaced fields.

Node implementation in `nodes/taxonomy_evaluator.py`:

- `_resolve_view(state, mode)` picks the right taxonomy view:
  - Test mode (`mode == "test"`): last `state.clusters[-1]` (the frozen seed).
  - Train mode: last `selected_clusters[-1]` when available, else `clusters[-1]`.
- `evaluate_taxonomy(state, config)`:
  - Reads configuration via `Configuration.from_runnable_config(config)`.
  - Short-circuits when `evaluation_enabled` is false, returning `{"evaluation": None, "status": ["Evaluation disabled ..."]}`.
  - Resolves the view; if empty, logs a warning and returns `evaluation=None` with a status message.
  - Samples up to `evaluation_max_documents` from `state.documents`.
  - Calls `run_scoreboard(view, documents, configuration)`.
  - Logs a warning when the returned scoreboard is unavailable.
  - Returns only:

    ```python
    {
        "evaluation": scoreboard,
        "status": [f"Evaluated taxonomy ({mode_label})."],
    }
    ```

**Invariants:** the node never writes `clusters`, `selected_clusters`, or any routing fields; it is strictly observe-only and safe to insert without affecting graph control flow.

### 4b. Postscript (2026-09-05): the graph.py edges were never actually added

The heading above this postscript — "Add an observe-only in-graph evaluation node" — describes the node, state field, and routing functions (`routing/should_continue_after_evaluation.py`: `should_evaluate_after_selection`, `should_continue_after_evaluation`) exactly as originally designed for this suite: train mode `select_dimensions → evaluate_taxonomy → label_documents`, test mode `label_documents → evaluate_taxonomy → aggregate_new_values`. All of that was genuinely built by the commit that introduced it (`1519860`, "wire observe-only evaluate_taxonomy node into the graph"). What that commit's diff actually touched, though, was only `nodes/taxonomy_evaluator.py`, `routing/should_continue_after_evaluation.py`, and `state.py` — **`graph.py` itself was never edited to call `builder.add_node`/`builder.add_edge` for this node.** The routing functions above sat unimported and unused, and `evaluate_taxonomy` never ran on a single live pipeline invocation, from that commit until this doc's `last_updated` date — roughly two weeks.

This went undetected for a structural reason, not an oversight in testing discipline: the node's own defining invariant — "observe-only, degrades gracefully, never fails the run" — means a *missing* node produces the exact same visible behavior as a *present-but-disabled* node. There was no crash, no failing test, no error to chase. The scoreboard panel/JSON/report code in `main.py` and `report_renderer.py` (Section 5 above) was fully built and worked correctly in isolation and via the standalone `--evaluate` CLI mode — it simply never received input from a live run, because nothing ever produced it.

It was found and fixed on branch `feat/taxonomy-evaluation-feedback-integration` (commit `83dacf2` as of this writing) while implementing a follow-on feature (feeding evaluation results into `format_feedback` for `update_taxonomy`/`review_taxonomy`) that needed to build on top of this exact wiring — reading `graph.py` to find the existing insertion point revealed it was never inserted. `graph.py` now registers the node under two names (`evaluate_taxonomy` for a new per-iteration loop-feedback call, `evaluate_taxonomy_final` reusing the original design's routing functions verbatim for the post-selection/post-labeling scoreboard), completing the topology this section describes.

**Lesson for future work in this codebase:** when a plan or a prior doc describes graph wiring ("node X is inserted between A and B"), verify the claim by reading `graph.py`'s actual `add_node`/`add_edge` calls directly — do not trust a commit message or a docstring alone, especially for an observe-only node, where "never wired in" and "wired in but doing nothing wrong" are indistinguishable from the outside.

### 5. Surface the scoreboard in the CLI and report

Two surfaces reuse the same scoreboard dict shape.

**CLI panel (terminal)**

`main.py` defines `_display_scoreboard(scoreboard, configuration)`:

- Early-return on `None` or `{}`.
- Special-cases `unavailable` scoreboards with a one-line panel explaining the error.
- For available scoreboards:
  - Renders a `Table` with columns *Criterion*, *Score*, *Pass*, *Reason*.
  - For evaluated rows, formats scores as `0.00`, derives pass marks from the threshold, and flattens multi-line reasons into single lines.
  - For non-evaluated rows (coverage without documents), renders `Score` and `Pass` as `—` with a fixed reason: `"Not evaluated — no documents provided."`.
  - Adds a panel subtitle recording `overall`, `model`, and `evaluation_threshold`.

**Report section**

`src/taxonomy_generator/report_renderer.py` adds `render_evaluation(scoreboard)` and threads it into `assemble_report` / `generate_and_write_report`:

- `render_evaluation(scoreboard)`:
  - Returns `""` when `scoreboard` is falsy, has `unavailable=True`, or has no criteria.
  - Otherwise, emits a deterministic markdown section:

    ```markdown
    ## Evaluation

    _Observe-only LLM-as-judge scoreboard (judge: <model>). Pass flags are display-only — nothing gates on them._

    | Criterion | Score | Pass | Reason |
    |---|---|---|---|
    | Orthogonality | 0.85 | ✓ | ... |
    | Dimensional coverage | — | — | Not evaluated — no documents provided. |
    ```

  - Appends an overall line when `overall` is present.

- `assemble_report(...)` takes an optional `evaluation` parameter and, when non-empty, appends the rendered Evaluation section after Discarded Dimensions.
- `generate_and_write_report(...)` receives the stored evaluation dict from callers (either in-graph or standalone `--report`) and passes it through to `assemble_report`.

### 6. Standalone `--evaluate` CLI mode

`main.py` implements `_run_evaluate(args)` to reuse the same runner and comparison logic outside the graph:

- Initializes settings via `init_settings(args.config)` and builds a minimal `Configuration` for output-dir resolution.
- Resolves an output directory via `visualization.resolve_output_dir(configuration)` and constructs a timestamped `evaluation_*.json` path using the same name-prefix convention as reports.
- **Single-file mode:**
  - Loads the taxonomy JSON via `_load_taxonomy_file`.
  - Selects the view and iteration via `_select_clusters_for_visualize(data, args.iteration)`.
  - Optionally loads a corpus via `load_corpus(args.corpus)` and wraps each string as a `{"content": ...}` doc for the coverage criterion.
  - Prints a header panel mirroring `_run_report`.
  - Calls `run_scoreboard` and passes the result to `_display_scoreboard`.
  - Writes the scoreboard dict to the evaluation JSON artifact.
- **Multi-file mode:**
  - Loads each taxonomy file and extracts its clusters.
  - Calls `compare_taxonomies([...], configuration)`.
  - Prints a consistency panel via `_display_consistency`.
  - Writes the comparison dict to the evaluation JSON artifact.

This mirrors the existing `--visualize` / `--report` pattern and means any saved taxonomy JSON can be scored or compared without rerunning the pipeline.

## Why This Matters

- **Turns vague quality criteria into inspectable signals.** The seven review criteria move from being one-off prompt text to stable, named metrics that can be inspected per run and compared over time.
- **Keeps evaluation strictly observe-only.** By routing evaluation through a dedicated node that never mutates routing state and by degrading to `unavailable` on failure, the suite adds quality signals without introducing new failure modes.
- **Supports both in-run and post-hoc workflows.** The same runner supports scoring during a pipeline run, scoring any saved taxonomy later, and comparing multiple runs for consistency, all via a consistent scoreboard shape.
- **Integrates cleanly with existing surfaces.** The evaluation field follows the four-step surfacing recipe documented in `surface-langgraph-node-output-through-state-schema-to-cli-and-report.md`: declare on `State`/`OutputState`, have a producing node write it, accumulate it in `main.py`, and render it in `report_renderer.py`.
- **Leaves room for future gates and loops.** Scoreboards accumulate across corpora and runs, giving future plans the calibration data needed for thresholds, gated deployments, or review-loop return arcs without committing to those behaviors now.

## When to Apply

Use this pattern when:

- You need to **add or adjust evaluation criteria** for the taxonomy while keeping the rest of the pipeline behavior unchanged.
- You want to **introduce a new evaluation mode** (e.g., additional coverage checks, alternative consistency heuristics) that should surface through the same scoreboard + report contract.
- You are adding **new observe-only analysis nodes** whose outputs should be visible in JSON and the grounded-theory report but must not route or terminate the graph.
- You are extending standalone CLI tooling to **score or compare artifacts produced by the pipeline** without re-running it.

It does **not** apply to changes that should gate or re-route the pipeline based on scores — those require additional design around thresholds and feedback loops.

## Examples

- **Adding a new structural criterion**
  - Extend `STRUCTURAL_CRITERIA` in `evaluation/metrics.py` with a new `Criterion` instance.
  - No runner changes needed as long as the criterion does not require documents.
  - The new criterion appears automatically in the CLI panel and report section.

- **Adding an additional data-grounded check**
  - Add a new `Criterion` with `needs_documents=True`.
  - `build_metrics(..., include_coverage=True)` will pick it up whenever documents are present.
  - The row will be marked `evaluated=False` and `score=None` when documents are unavailable, matching the existing coverage behavior.

- **Experimenting with a different consistency threshold**
  - Tune `evaluation_consistency_threshold` and `evaluation_consistency_borderline_band` in settings.
  - The `compare_taxonomies` logic remains unchanged; only which pairs get aligned vs sent to the judge moves.
  - Agreement and recurring/one-off groupings reflect the new threshold.

- **Extending another observe-only node**
  - Follow the same shape as `evaluate_taxonomy`: read configuration from `RunnableConfig`, resolve the view, sample a bounded number of documents, call a pure helper (runner), and return only a new field plus a status message.
  - Surface the new field using the four-step recipe in the related architecture-pattern doc.

## Related

- `docs/plans/2026-08-20-0031-feat-taxonomy-evaluation-suite-plan.md` — unified plan that defines the evaluation suite's requirements, key technical decisions, implementation units, and verification contract.
- `docs/plans/2026-09-05-1905-feat-taxonomy-evaluation-feedback-integration-plan.md` — the follow-on plan that discovered and completed the missing `graph.py` wiring (see the postscript above) while adding per-iteration feedback into `format_feedback`.
- `docs/solutions/architecture-patterns/surface-langgraph-node-output-through-state-schema-to-cli-and-report.md` — the four-step recipe this pattern reuses to surface the `evaluation` field into JSON and reports.
- `docs/solutions/integration-issues/deepeval-geval-temperature-unsupported-on-newer-openai-models.md` — a bug in this suite's judge-model integration that stayed latent until the postscript above's fix made `evaluate_taxonomy` actually run for the first time.
- `docs/solutions/logic-errors/html-report-ignores-embedded-evaluation-scoreboard.md` — a second gap this same live-run exposed: `--html-report` never read the taxonomy JSON's own embedded `evaluation` key.
- `CONCEPTS.md` — entries for **Scoreboard**, **Consistency Comparison**, and **Observe-Only Evaluation** define the shared vocabulary this suite uses.
