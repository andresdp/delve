# Option A1 Plan: Integrate Taxonomy Evaluation Feedback into the Main Graph

## Objective

Integrate automated taxonomy evaluation into the existing LangGraph workflow so that evaluation outcomes are fed back into taxonomy improvement steps via existing prompt feedback channels (Option A1), evaluating on **every** axial-coding iteration (not throttled) so `update_taxonomy` gets fresh signal each pass — while still producing the single, final scoreboard the report/JSON/panel surfaces already expect.

This plan:

1. Runs `evaluate_taxonomy` after every `generate_taxonomy`/`update_taxonomy` pass, feeding a history that `format_feedback` reads from.
2. Finishes the pre-existing (but never-wired) post-selection evaluation call so the pipeline's already-built reporting surfaces start receiving real data.
3. Extends `format_feedback(state)` with a human-readable evaluation summary built from the evaluator's actual scoreboard shape.
4. Lets `update_taxonomy` and `review_taxonomy` automatically leverage those signals through current prompt wiring — no new prompt variables.

---

## Current Baseline (corrected)

This is not a from-scratch integration. A prior plan — [`docs/plans/2026-08-20-0031-feat-taxonomy-evaluation-suite-plan.md`](2026-08-20-0031-feat-taxonomy-evaluation-suite-plan.md) (KTD6) — already designed and mostly built this:

- `taxonomy_evaluator.py` (`evaluate_taxonomy`) exists, is observe-only, and returns `{"evaluation": scoreboard, "status": [...]}`. Its docstring and `_resolve_view` describe scoring "the final (post-selection) view" — accurate for KTD6's intended placement, not for the mid-loop placement this plan adds. Needs updating for both.
- `state.py` already has `evaluation: Optional[Dict]` on `OutputState`/`State`, documented as "replace semantics — set once."
- `routing/should_continue_after_evaluation.py` already implements the KTD6 routing (`should_evaluate_after_selection`, `should_continue_after_evaluation`) for train: `select_dimensions → evaluate_taxonomy → label_documents`, test: `label_documents → evaluate_taxonomy → aggregate_new_values`. **It is currently imported nowhere** — dead code, not because the design was abandoned, but because commit `1519860` ("wire observe-only evaluate_taxonomy node into the graph") added the node, state field, and routing functions but never added the corresponding `graph.py` edges.
- `main.py` already has the *entire* downstream surface built and working: the `evaluate_taxonomy` `STEP_INFO` entry, the `astream`-loop accumulation of `"evaluation"`, the `_display_scoreboard` rich panel, the JSON-artifact and taxonomy-JSON `evaluation` key, and the report section threading (`report_renderer.render_evaluation`). None of it has ever fired during a live pipeline run, because `graph.py` never calls the node — it only works today via the standalone `--evaluate`/`--report` CLI paths.
- The actual scoreboard shape (`evaluation/runner.py::run_scoreboard`) is a **flat** dict:
  ```json
  {"criteria": [{"name": "...", "description": "...", "threshold": 0.5, "evaluated": true, "score": 0.74, "passed": true, "reason": "..."}],
   "overall": 0.78, "model": "gpt-...", "unavailable": false}
  ```
  Criteria names are exactly: `Orthogonality`, `Clarity`, `Completeness`, `Use case alignment`, `No catch-alls`, `Axis vs. value`, `Dimensional coverage` (`evaluation/metrics.py`). **There is no per-dimension/per-cluster score and no drift field.** An earlier draft of this plan assumed metrics that don't exist in the code — corrected below.
- `graph.py` genuinely does not register or route through `evaluate_taxonomy` today — that part of the original baseline was accurate.

---

## Design Choice (Option A1, revised)

Register the **same** `evaluate_taxonomy` node under two node names, each wired at a different point, serving two different consumers:

1. **Loop call** (`"evaluate_taxonomy"`, new) — after every `generate_taxonomy`/`update_taxonomy`, before `check_saturation`. Purpose: keep `update_taxonomy` (next iteration) and `review_taxonomy` (right after the loop exits) supplied with fresh, iteration-fresh feedback via `format_feedback`. Runs on every pass, by explicit choice — the added judge-call cost is accepted in exchange for iterative signal (see Risks).
2. **Final call** (`"evaluate_taxonomy_final"`, finishing KTD6) — `select_dimensions → evaluate_taxonomy_final → label_documents` (train) / `label_documents → evaluate_taxonomy_final → aggregate_new_values` (test), reusing `should_evaluate_after_selection` / `should_continue_after_evaluation` verbatim. Purpose: produce the canonical scoreboard for the reporting surfaces that already exist in `main.py` and expect one final, stable `state.evaluation`.

Both node names point at the identical `evaluate_taxonomy` function — no forked logic. Because `state.evaluation` has plain replace semantics (no reducer) and this graph is a strict sequential chain (no parallel branches touching it), whichever call executes last wins. The final call always executes after every loop call in both modes, so `state.evaluation` naturally ends up holding the true final scoreboard with zero special-casing — `main.py`'s existing consumers keep working unmodified.

A new `evaluation_history` field accumulates **every** call from both sites, in execution order. `format_feedback` reads `evaluation_history[-1]` — always the freshest available scoreboard at the moment a prompt is built, whether that's a mid-loop draft (for `update_taxonomy`'s next pass, or for `review_taxonomy` right after the loop) or, for any later consumer, the final one.

Benefits over the original draft:

- Reuses 100% of the already-built KTD6 scaffolding instead of leaving it dead.
- Keeps `state.evaluation`'s existing "final, stable" contract intact — `main.py`'s panel/JSON/report code needs no changes.
- `format_feedback`'s example output is now grounded in the real scoreboard schema.

---

## Implementation Plan

### 1) Wire the loop-feedback call

**Files:** `src/taxonomy_generator/graph.py`

```python
from taxonomy_generator.nodes.taxonomy_evaluator import evaluate_taxonomy

builder.add_node("evaluate_taxonomy", evaluate_taxonomy)
```

Replace:
```python
builder.add_edge("generate_taxonomy", "check_saturation")
builder.add_edge("update_taxonomy", "check_saturation")
```
with:
```python
builder.add_edge("generate_taxonomy", "evaluate_taxonomy")
builder.add_edge("update_taxonomy", "evaluate_taxonomy")
builder.add_edge("evaluate_taxonomy", "check_saturation")
```

This node call is unconditional in the topology, but `evaluate_taxonomy` already early-returns without any judge calls when `evaluation.enabled` is false (see Step 3) — so a disabled config still adds a graph hop per iteration but does no LLM work.

### 2) Finish the final-call wiring (completes KTD6)

**Files:** `src/taxonomy_generator/graph.py`, `src/taxonomy_generator/routing/should_aggregate_values.py`

```python
from taxonomy_generator.routing.should_continue_after_evaluation import (
    should_continue_after_evaluation,
    should_evaluate_after_selection,
)

builder.add_node("evaluate_taxonomy_final", evaluate_taxonomy)
```

Replace the train-mode edge:
```python
builder.add_edge("select_dimensions", "label_documents")
```
with:
```python
builder.add_conditional_edges(
    "select_dimensions",
    should_evaluate_after_selection,
    {
        "evaluate_taxonomy": "evaluate_taxonomy_final",
        "label_documents": "label_documents",
    },
)
builder.add_conditional_edges(
    "evaluate_taxonomy_final",
    should_continue_after_evaluation,
    {
        "label_documents": "label_documents",
        "aggregate_new_values": "aggregate_new_values",
    },
)
```

Extend `should_aggregate_values` (test-mode path) to detour test-mode runs through the final evaluator call before aggregation, matching KTD6's `test: label_documents → evaluate_taxonomy → aggregate_new_values`:

```python
def should_aggregate_values(state: State, config: RunnableConfig) -> Literal["evaluate_taxonomy", "aggregate_new_values", "__end__"]:
    configuration = Configuration.from_runnable_config(config)
    if configuration.mode == "test":
        return "evaluate_taxonomy" if configuration.evaluation_enabled else "aggregate_new_values"
    return "__end__"
```
with the corresponding `add_conditional_edges` mapping updated to route `"evaluate_taxonomy"` to `"evaluate_taxonomy_final"`.

`evaluation.enabled: false` restores today's exact topology in both spots via the existing routing functions' fallthrough — verified by the Validation Checklist.

### 3) Update the evaluator's return payload and docstrings

**Files:** `src/taxonomy_generator/nodes/taxonomy_evaluator.py`, `src/taxonomy_generator/state.py`

Update the module docstring to describe both call sites (loop draft-scoring vs. final post-selection scoring) instead of only "the final view."

Return payload, every call:
```python
return {
    "evaluation": scoreboard,
    "evaluation_history": [scoreboard],
    "status": [f"Evaluated taxonomy ({mode_label})."],
}
```
Disabled/skipped branches return `"evaluation_history": []` (no-op for the reducer) rather than appending `None`.

`state.py` — follow the repo's existing accumulation convention (used by `clusters`, `explanations`, `status`, `open_codes`, `saturation_history`) instead of manual list concatenation:
```python
evaluation_history: Annotated[List[Dict], operator.add] = field(default_factory=list)
```
Keep `evaluation`'s existing field and docstring as-is on `OutputState`/`State` — its "replace, set once" contract is still correct; it's the *final* call that sets it last, by construction (Design Choice above).

### 4) Extend `format_feedback(state)` with a real evaluation summary

**Files:** `src/taxonomy_generator/utils.py`

1. Read `state.evaluation_history[-1]` if present.
2. Skip it entirely if absent, or if `.get("unavailable")` is true (degrade silently — R7's contract).
3. Sort `criteria` (excluding `evaluated: false` rows) ascending by `score`; surface the overall and the weakest few.
4. Append a concise section to existing feedback.

Corrected example, matching the real scoreboard shape:

```text
Automated evaluation summary for the current taxonomy (overall 0.71):
- Dimensional coverage: 0.62
- Axis vs. value: 0.65
- Orthogonality: 0.67
- Clarity: 0.74
- Completeness: 0.81
- Use case alignment: 0.85
- No catch-alls: 0.90

Please prioritize improving the lowest-scoring criteria above (especially
any below the configured threshold), while preserving dimensions that
already score well.
```

Optionally include the `reason` text for only the single weakest criterion, truncated, to keep the prompt short (existing "Prompt bloat" risk mitigation).

Because both `update_taxonomy` and `review_taxonomy` already consume `format_feedback(state)`, no prompt signature changes are required.

---

## Node-level behavior impact

- `update_taxonomy`: receives fresh, per-iteration evaluation-informed feedback via `evaluation_history[-1]` — this is new and is the actual point of this plan.
- `review_taxonomy`: runs right after the loop exits, before `select_dimensions`/the final call — it sees the *last loop iteration's* scoreboard (still fresh, just not the post-selection one), via the same `evaluation_history[-1]` read.
- `taxonomy_evaluator`: unchanged — still non-blocking, fault-tolerant, never writes `clusters`/`selected_clusters`/routing flags.

---

## Validation Checklist

1. Graph compiles with both `evaluate_taxonomy` and `evaluate_taxonomy_final` node registrations and all new edges: `python -c "from taxonomy_generator.graph import graph"`.
2. A full train run logs the evaluator after each `generate_taxonomy`/`update_taxonomy` pass *and* once more between `select_dimensions` and `label_documents`.
3. A full test run logs the evaluator once, between `label_documents` and `aggregate_new_values`.
4. `state.evaluation_history` grows by exactly one entry per loop iteration plus one final entry.
5. `state.evaluation` at run end equals `evaluation_history[-1]` exactly (the final call always wins, chronologically) — this is what `main.py`'s existing panel/JSON/report already consume, unmodified.
6. `format_feedback(state)` includes the evaluation summary only when a non-unavailable entry exists in `evaluation_history`, using real criteria names and scores (no fabricated fields).
7. `update_taxonomy` and `review_taxonomy` execute unchanged and receive enriched feedback text.
8. `evaluation.enabled: false`: both routing functions fall through to the direct edges; the loop-call node still executes but does no LLM work and appends nothing to `evaluation_history` — pipeline behavior and outputs are otherwise identical to today.
9. A judge failure mid-loop (`scoreboard.get("unavailable")`) does not fail the run, does not corrupt state, and is skipped by `format_feedback` rather than surfaced as noise.

---

## Risks & Mitigations

- **Risk: Per-iteration judge cost.** Running the full ~6-7 GEval criteria on every axial-coding pass (not just once) multiplies judge-call cost and latency by the loop's iteration count — potentially 5-20x a once-per-run design, depending on corpus size and the saturation streak threshold. **Accepted by explicit choice** for this plan, since iterative feedback is the goal `update_taxonomy` needs. Existing `evaluation.enabled`/`evaluation.max_documents` config remain the off-switches; a future cadence knob (evaluate every Kth iteration) is a trivial follow-up if cost becomes a problem, not required now.
- **Risk: Mid-loop scores are drafts, not final quality.** During the loop, `_resolve_view` in train mode always falls back to `clusters[-1]` (raw, unselected) since `selected_clusters` is empty until `select_dimensions` runs later — this is now the *intended* behavior for the loop call (scoring the current draft), but would be wrong if mistaken for the report's "final" number. **Mitigated** by the two-call-site design: `state.evaluation` (used by reporting) is only ever set last by the final call; `evaluation_history` (used by feedback) intentionally includes the drafts.
- **Risk: Scoreboard schema variability.** Mitigation: defensive `.get(...)` extraction in `format_feedback`, tolerate missing/`evaluated: false` rows.
- **Risk: Prompt bloat from verbose metrics.** Mitigation: limit the summary to the overall score plus all criteria sorted weakest-first (7 short lines), optionally one truncated `reason`.
- **Risk: Over-correction toward low-scoring criteria each iteration.** Mitigation: explicit instruction in the appended text to preserve already-strong dimensions.

---

## Out of Scope (for this iteration)

- Evaluation-driven routing/termination decisions (still strictly observe-only, per R6).
- New dedicated prompt variables for the evaluation payload.
- A/B multi-taxonomy evaluation orchestration.
- A configurable evaluation cadence (every-Kth-iteration throttling) — noted as a future mitigation, not built now.

---

## Deliverable Summary

After implementation, every axial-coding pass produces a fresh evaluation scoreboard that flows into `update_taxonomy`'s and `review_taxonomy`'s existing feedback channel, while the pipeline also completes the previously half-wired final evaluation call so the report, JSON artifact, and terminal panel — already built in `main.py` — start receiving real data for the first time in a live run.
