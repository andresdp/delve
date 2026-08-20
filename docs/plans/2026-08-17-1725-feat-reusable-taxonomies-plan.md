---
title: Reusable Taxonomies - Plan
type: feat
date: 2026-08-17
topic: reusable-taxonomies
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-brainstorm
execution: code
---

# Reusable Taxonomies - Plan

## Goal Capsule

- **Objective:** Let a Delve run start from a saved taxonomy and operate in two modes — train (refine the seeded taxonomy on a new corpus) and test (frozen dimensions, classify new documents, allow value growth, no-fit docs to the fallback bucket) — with optional user feedback and a test-mode delta summary.
- **Product authority:** This plan owns NEW_IDEAS items 1 and 2 (bootstrap from existing taxonomy; train/test modes). The evaluation suite (multi-run consistency + LLM-as-judge scoreboard), the review-loop return arc, and design-space solution sampling are not active scope.
- **Open blockers:** None. Product Contract unchanged; both deferred questions (OQ1 near-duplicate appends, OQ2 delta-summary surface) resolved during planning as KTD5 and KTD6.
- **Stop conditions:** Ship when every unit's verification passes and the Definition of Done holds. Do not expand into the parked NEW_IDEAS areas.

---

## Product Contract

### Summary

Delve runs become reusable: a saved taxonomy JSON seeds a new run, which then either continues refining it (train) or classifies new documents against it without touching its dimensions (test, with value growth and a delta summary). Optional user feedback flows into the existing feedback plumbing.

### Problem Frame

Every Delve run today generates a taxonomy from scratch, even when a good one already exists. The saved taxonomy outputs can only be rendered (`--report`, `--visualize`) — they cannot seed a new run. Classifying a fresh batch of documents against an existing taxonomy, the natural way to reuse it, is impossible without regenerating the taxonomy and hoping it converges somewhere similar. The `UserFeedback` state field and `{feedback}` prompt slot exist but nothing outside a run can populate them.

### Key Decisions

- KD1. One mode-aware graph, not a separate test graph or a CLI-only classify mode. (session-settled: user-approved — chosen over separate graph and CLI standalone modes: single entry point keeps CLI, deployment, outputs, and reporting working unchanged for both modes.) Governs R3, R4, R5.
- KD2. Test mode freezes dimensions but allows value growth; no-fit documents go to the existing predefined fallback bucket ("Other"). (session-settled: user-directed — chosen over pure labeling and full freeze.) Governs R5, R6, R7.
- KD3. Bootstrap input is the existing saved-taxonomy JSON format, always taking the final (or only) iteration. (session-settled: user-directed — chosen over iteration-selectable or a new flattened format.) Governs R1.
- KD4. Feedback arrives as a CLI flag, a file path, or inline `config.yaml` text — no interactive pause-and-collect. (session-settled: user-directed — chosen over HITL interrupt and structured-JSON payload.) Governs R8.
- KD5. Test mode runs no taxonomy-refinement stages (open coding, generation, update, review, consolidation, selection); appended values are deduplicated per KTD5.
- KD6. Evidence in test mode: a new value records the documents that prompted it as supporting evidence; evidence for existing values is derived from the labeled-documents output rather than by mutating the source taxonomy in place.

### Requirements

**Bootstrap input**

- R1. A run accepts a saved taxonomy JSON file as input and seeds the loaded final (or only) iteration as its starting taxonomy.
- R2. Without a taxonomy input, pipeline behavior is unchanged from today.

**Run modes**

- R3. A mode setting selects `train` (default) or `test`, overridable by CLI and `config.yaml` per the existing precedence chain.
- R4. In train mode with a seeded taxonomy, refinement continues from the seed through the existing open-code → update → saturation loop, and provided feedback flows into the existing feedback slot consumed by update and review prompts.
- R5. In test mode, dimensions are frozen: no dimension is added, renamed, merged, split, or dropped.

**Test-mode classification**

- R6. In test mode, each new document is classified into an existing dimension, or recorded under the predefined fallback category when no dimension fits.
- R7. In test mode, when a document's specific decision does not fit any existing value of its dimension, a new value may be appended to that dimension, recording the triggering document(s) as supporting evidence.

**Feedback input**

- R8. Optional user feedback is accepted as a CLI flag, a file path, or inline `config.yaml` text, and reaches the same `{feedback}` prompt slot as existing feedback.

**Outputs**

- R9. Test mode emits the standard labeled-documents output plus a delta summary: new values per dimension and the fallback-bucket document list.
- R10. Test mode's taxonomy output preserves all seeded dimensions unchanged, differing from the input only by value additions.

### Key Flows

- F1. Train run from a saved taxonomy
  - **Trigger:** Mode `train` with a taxonomy input.
  - **Steps:** Load corpus → seed taxonomy from saved JSON → (summarize) → minibatch → open code → update (seeded, never initial generation) → saturation check → loop or review → consolidate → select → label.
  - **Outcome:** A refined taxonomy whose history starts from the seeded iteration. Covers R1, R4.
- F2. Test run
  - **Trigger:** Mode `test` with a taxonomy input.
  - **Steps:** Load corpus → load frozen taxonomy → (skip summarize and minibatching) → classify all documents (two-level: dimension, then value; fallback to "Other") → aggregate new values (dedup, append, delta summary).
  - **Outcome:** Labeled documents; taxonomy unchanged except appended values. Covers R5, R6, R7, R9, R10.

### Acceptance Examples

- AE1. **Train bootstrap starts at update.** Given a saved taxonomy and mode `train`, the first axial pass after open coding is an incremental update of the seeded dimensions, not initial generation. Covers R1, R4.
- AE2. **No-fit document in test mode.** Given a document that fits no dimension, the run labels it with the fallback category and lists it in the delta summary. Covers R6, R9.
- AE3. **Value growth in test mode.** Given a document that fits dimension D1 but whose decision matches no existing value of D1, D1 gains one new value naming that decision with the document as supporting evidence; D1's other values and all other dimensions are unchanged. Covers R5, R7, R10.
- AE4. **Feedback from config.** Given inline feedback text in `config.yaml`, a train run's update and review prompts receive it in the feedback slot. Covers R8.
- AE5. **Fresh run unaffected.** Given no taxonomy input, the run generates a taxonomy from scratch exactly as today. Covers R2.

<!-- ce-section: work-relationships -->
### How This Work Fits Together

This plan owns **reusable taxonomies** (NEW_IDEAS items 1–2). The surrounding breakdown below is the current understanding, not a committed roadmap; later plans may revise, split, merge, or discard these areas.

- Evaluation suite (NEW_IDEAS items 4–5: multi-run consistency, LLM-as-judge scoreboard) — **Depends on** this plan: test mode gives the suite a fixed taxonomy to score new data against; the scoreboard's standalone mode could later consume test-mode delta summaries.
- Review-loop return arc (item 6) — **Can proceed independently of** this plan; both touch graph routing but not the same edges.
- Design-space solution sampling (item 7) — **Can proceed independently**; consumes the consolidated Values this feature preserves in test mode.
- Parked items remain contextual candidates; none are Requirements here (see Scope Boundaries).

### Scope Boundaries

- Evaluation suite (multi-run consistency assessment, LLM-as-judge scoreboard) — parked, separately planned.
- Review-node return arc / saturation-vs-review rework — parked, separately planned.
- Design-space solution sampling across dimension values — parked, separately planned.
- Interactive human-in-the-loop feedback (pause at review, collect, resume).
- Borderline-band LLM adjudication of test-mode value appends (auto-map-or-append only in this pass; see KTD5).
- Extending the grounded-theory report renderer with a delta-summary section (the report renders the value-extended final iteration unchanged; a dedicated delta section can ride the parked evaluation-suite work).

### Dependencies / Assumptions

- Two-level labeling is not wired today: `LabelOutput` carries no value and `doc_labeler.py` never populates `Doc.value`, even though `Value` and `Doc.value` exist. Test mode's value assignment requires extending labeling to dimension + value (U3). Verified against `src/taxonomy_generator/schemas.py` and `src/taxonomy_generator/nodes/doc_labeler.py`.
- Train-mode seeding reuses the existing routing primitive: `should_generate_or_update` already routes to `update_taxonomy` when clusters exist. Verified against `src/taxonomy_generator/routing/should_generate_or_update.py`.
- The fallback bucket exists as `fallback_category: "Other"` in `config.yaml`; test mode reuses it rather than introducing a new bucket concept.
- A bootstrapped train run may exit refinement quickly when the seeded taxonomy already saturates on the new corpus; that is intended loop behavior, not a defect.
- The labeler reads raw `doc.content` today, not summaries — summaries only feed taxonomy generation, so test mode loses nothing by skipping summarization.

### Sources / Research

- `docs/NEW_IDEAS.md` — items 1 and 2 are the origin of this scope.
- `docs/DESIGN.md` and `docs/TAXONOMY_QUALITY_PLAN.md` — pipeline shape, value/relation model, build order context.
- `src/taxonomy_generator/state.py` — `InputState` (documents only), `UserFeedback`, `Doc.value`.
- `src/taxonomy_generator/graph.py` — current topology and conditional edges.
- `src/taxonomy_generator/nodes/doc_labeler.py`, `src/taxonomy_generator/schemas.py` — labeling gap.
- `src/taxonomy_generator/nodes/value_consolidator.py` and `src/taxonomy_generator/visualization.py` — embedding-loading pattern and distance-threshold precedent for test-mode dedup.
- `config.yaml`, `src/taxonomy_generator/settings.py`, `src/taxonomy_generator/configuration.py` — settings layering and the add-a-setting convention.
- `main.py` — CLI flags, streaming accumulation, output serialization, `--visualize`/`--report` standalone precedent (`_select_clusters_for_visualize`).

---

## Planning Contract

### Key Technical Decisions

- KTD1. **Seed enters state as the first cluster iteration, emitted by `load_corpus`.** `load_corpus` reads the seed path from configuration, loads the final iteration's clusters via a new `load_seed_taxonomy()` util, and returns them as `clusters: [seed]` with a paired explanation ("Seeded taxonomy from `<path>` — N dimensions"). The `operator.add` accumulator and the existing `should_generate_or_update` routing then make every subsequent axial pass an `update_taxonomy` pass with zero routing changes. Governs R1, R4.
- KTD2. **`should_summarize` becomes the three-way post-load router.** Mode `test` routes `load_corpus → label_documents` directly, skipping summarization and minibatching — the labeler reads raw content today, and summaries only feed taxonomy generation. Train keeps the existing two-way behavior. Governs R3, R5.
- KTD3. **External feedback is a persistent channel, not a reuse of `state.user_feedback`.** `InputState` gains `user_feedback`; `format_feedback()` merges it (external first, automated-critic content second) so it reaches update and review prompts for the whole run instead of being silently overwritten by the first saturation check. Governs R8, R4.
- KTD4. **Two-level labeling via a `value_label` field on `LabelOutput`, in both modes.** The labeler prompt instructs: pick the best existing value of the assigned dimension, or propose a concise new value label when none fits; null when the fallback category is used. `Doc.value` is populated accordingly. In train mode proposals live on documents only (the taxonomy keeps evolving anyway); test mode aggregates them (KTD5). (session-settled: user-approved — chosen over test-mode-only labeling: the serialized `value` field exists today and both modes benefit.) Governs R6, R7.
- KTD5. **Test-mode dedup: embed each proposal against its dimension's existing values; below `value_merge_distance_threshold` map to the nearest existing value, otherwise append.** Proposals are also deduplicated among themselves with the same threshold so repeated new decisions collapse into one value. Borderline-band LLM adjudication is deliberately deferred (Scope Boundaries) to keep test runs cheap. (session-settled: user-approved — chosen over raw append: repeated new decisions should collapse into one value.) Governs R7, R10.
- KTD6. **Delta summary renders as a rich CLI panel and a `delta_summary` section in the saved taxonomy JSON.** The grounded-theory report is not extended in this pass. (session-settled: user-approved — chosen over report integration: report already renders the value-extended final iteration.) Governs R9.
- KTD7. **Test-mode taxonomy output is two iterations: the seed, then the value-extended seed.** A new `aggregate_new_values` node (test mode only) returns the updated clusters as a new iteration with a paired explanation; `selected_clusters` stays absent because `select_dimensions` never runs, so `--report`/`--visualize` default to the value-extended last iteration. Governs R10, R9.

### High-Level Technical Design

Mode-aware graph topology (new/changed elements in bold conceptually — see U5 for exact wiring):

```mermaid
flowchart TB
    START([START]) --> load[load_corpus — seeds clusters[0] when taxonomy_input set]
    load --> route1{should_summarize — extended with mode}
    route1 -->|test mode| label[label_documents — two-level: dimension + value]
    route1 -->|train, skip=false| sum[summarize]
    route1 -->|train, skip=true| batch[get_minibatches]
    sum --> batch
    batch --> open[open_code_minibatch]
    open --> genupd{should_generate_or_update}
    genupd -->|no clusters| gen[generate_taxonomy]
    genupd -->|clusters exist — seeded runs land here| upd[update_taxonomy]
    gen --> sat[check_saturation]
    upd --> sat
    sat -->|continue| open
    sat -->|saturated or exhausted| rev[review_taxonomy]
    rev --> cons[consolidate_values]
    cons --> sel[select_dimensions]
    sel --> label
    label --> route2{should_aggregate_values — new}
    route2 -->|test mode| agg[aggregate_new_values — dedup, append, delta summary]
    route2 -->|train mode| END([END])
    agg --> END
```

State and schema deltas:

- `InputState` + `user_feedback: Optional[UserFeedback]` — external feedback enters via `invoke_input` (KTD3).
- `OutputState` + `delta_summary: Optional[Dict]` — emitted by `aggregate_new_values`; `main.py` accumulates it from the stream like `saturation_history`.
- `LabelOutput` + `value_label: Optional[str]` (KTD4).
- Settings: `PipelineSettings` + `mode: str = "train"`, `taxonomy_input: Optional[str] = None`; new `FeedbackSettings` (`text`, `file`) consumed by `main.py`; `Configuration` + `mode`, `taxonomy_input` (routing and `load_corpus` read them; feedback does not need a `Configuration` field).

---

## Implementation Units

### U1. Settings and taxonomy seeding

- **Goal:** A run can load a saved taxonomy JSON as its starting taxonomy; mode/taxonomy-input/feedback settings exist end to end.
- **Requirements:** R1, R2, R3 (settings half)
- **Dependencies:** None.
- **Files:** `src/taxonomy_generator/settings.py`, `src/taxonomy_generator/configuration.py`, `config.yaml`, `SETTINGS.md`, `src/taxonomy_generator/utils.py`, `src/taxonomy_generator/nodes/corpus_loader.py`, `pyproject.toml`, `requirements.txt`, `tests/unit_tests/test_taxonomy_seeding.py`
- **Approach:**
  1. Add `mode` and `taxonomy_input` to `PipelineSettings`, `FeedbackSettings` (`text`, `file`), the `config.yaml` sections, `Configuration` fields + `_defaults_from_settings`, and `SETTINGS.md` entries (repo convention: all four places).
  2. Add `load_seed_taxonomy(path)` to `utils.py`: accept the saved format (`{"iterations": [...]}` → last iteration's `clusters`) and a bare cluster list; deliberately ignore `selected_clusters` (per KD3, final iteration is authoritative); raise `ValueError` on missing file, no iterations, or an empty/non-dict cluster list.
  3. In `load_corpus`: when `taxonomy_input` is set, load the seed and return `clusters: [seed]` plus a paired `explanations` entry; validate that `mode == "test"` requires `taxonomy_input` (raise `ValueError` early). No seed → behavior byte-identical to today (R2).
  4. Add `pytest` and `pytest-asyncio` as dev dependencies in `pyproject.toml` and `requirements.txt` (repo rule: both files); the Makefile already targets `tests/unit_tests/`.
- **Test scenarios:**
  - Covers R1. Seed file with 3 iterations loads only the last iteration's clusters as `clusters[0]`.
  - File containing `selected_clusters` — selection is ignored, final iteration is seeded.
  - Bare cluster-list file loads directly.
  - Empty `iterations`, missing file, and empty cluster list each raise `ValueError` with a path-naming message.
  - `mode=test` without `taxonomy_input` raises before any LLM work.
  - Seeded load pairs `explanations[0]` with the seed iteration (index pairing preserved).
  - No-seed `load_corpus` output equals today's (documents + status only).
- **Verification:** `make test` passes for the new module; a seeded `load_corpus` call returns the seed as `clusters[0]` with a paired explanation.

### U2. External feedback channel

- **Goal:** Operator-provided feedback reaches the `{feedback}` slot of update and review prompts for the whole run.
- **Requirements:** R8, R4 (feedback half)
- **Dependencies:** U1 (settings section exists).
- **Files:** `src/taxonomy_generator/state.py`, `src/taxonomy_generator/utils.py`, `tests/unit_tests/test_feedback.py`
- **Approach:**
  1. Add `user_feedback: Optional[UserFeedback]` to `InputState` (keep `State`'s existing declaration, mirroring the `documents` pattern).
  2. Extend `format_feedback()` to merge both sources when present: external feedback first ("User feedback: ..."), then the automated critic's `state.user_feedback` content; "None." only when both are absent (KTD3).
  3. No prompt-file changes needed — the merged text flows through the existing `{feedback}` partials in generate/update/review.
- **Test scenarios:**
  - No feedback of either kind → "None."
  - External feedback only → included, prefixed "User feedback:".
  - Automated critic only → today's rendering unchanged.
  - Both present → external first, critic second, both visible.
  - `UserFeedback` with an invalid `decision` value fails Pydantic validation.
- **Verification:** `make test` passes; a state carrying external feedback renders it through `format_feedback` alongside critic feedback.

### U3. Two-level labeling

- **Goal:** Every labeled document carries a value (existing or newly proposed) alongside its dimension.
- **Requirements:** R6, R7 (proposal half)
- **Dependencies:** U1 (settings only for `fallback_category` read, already present).
- **Files:** `src/taxonomy_generator/schemas.py`, `src/taxonomy_generator/prompts/labeler.md`, `src/taxonomy_generator/nodes/doc_labeler.py`, `tests/unit_tests/test_labeler.py`
- **Approach:**
  1. Add `value_label: Optional[str]` to `LabelOutput` with field guidance: best existing value of the assigned dimension from `taxonomy_json`; a concise new label when none fits; null when the fallback category is used (KTD4).
  2. Update `prompts/labeler.md`: after choosing the dimension, choose among that dimension's `values` (already serialized by `format_taxonomy`); propose a new value label only when no existing value fits.
  3. Populate `Doc.value` in the labeler's reconstruction; include the value in `_format_results` output.
- **Test scenarios:**
  - Covers AE3 (proposal half). Document whose decision matches an existing value → `value_label` equals that value's label.
  - Document whose decision fits no existing value → a non-empty proposed `value_label`.
  - Document routed to the fallback category → `value_label` is null and `Doc.value` is None.
  - All docs get `Doc.value` populated from `value_label` (mocked chain returning fixed `LabelOutput`s).
  - Results formatter renders the value line for a labeled doc.
- **Verification:** `make test` passes; a mocked labeling pass over two docs yields correct `category`/`value` pairs.

### U4. Value aggregation node (test mode)

- **Goal:** Test-mode value proposals are deduplicated, appended to the frozen dimensions with supporting evidence, and summarized as a delta.
- **Requirements:** R7, R9, R10
- **Dependencies:** U3 (proposals exist), U1 (embedding + threshold settings exist).
- **Files:** `src/taxonomy_generator/nodes/value_aggregator.py` (new), `src/taxonomy_generator/state.py` (`delta_summary` in `OutputState`), `tests/unit_tests/test_value_aggregator.py`
- **Approach:**
  1. New `aggregate_new_values(state, config)`: collect docs with a real category and a `value_label` not matching (case-insensitive) an existing label of that dimension → candidates grouped by dimension.
  2. Embed candidates and existing values per dimension (reuse the embedding-loading pattern from `value_consolidator.py`/`visualization.py`); candidate below `value_merge_distance_threshold` from an existing value maps onto it; survivors dedup among themselves with the same threshold (KTD5).
  3. Append surviving values to their dimension with `supporting_doc_ids` from contributing docs; value ids continue the dimension's existing id scheme.
  4. Return the updated clusters as a new iteration with a paired explanation, plus `delta_summary` = `{"new_values": [{dimension, value, supporting_doc_ids}], "fallback_documents": [{id, preview}]}` (KTD7).
  5. Embedding failure degrades gracefully: log a warning, fall back to exact-string dedup only — never fail the run.
- **Test scenarios:**
  - Covers AE3. Far-from-existing proposal → one new value appended once, with the triggering doc id as support; dimension's other values and all other dimensions unchanged.
  - Covers AE2. Fallback documents appear in `delta_summary.fallback_documents` and are never value candidates.
  - Near-duplicate proposal (mocked embeddings below threshold) maps onto the existing value; no append.
  - Two docs proposing near-identical labels collapse into one appended value with both doc ids.
  - No candidates → empty `new_values`, clusters iteration still emitted (output-shape stability).
  - Embedding loader raising → exact-string dedup path, warning logged, run succeeds.
- **Verification:** `make test` passes; a scripted state with mixed proposals produces the expected appended values and delta.

### U5. Graph wiring for run modes

- **Goal:** The single graph routes train and test runs correctly.
- **Requirements:** R3, R5
- **Dependencies:** U1 (mode setting), U4 (aggregation node).
- **Files:** `src/taxonomy_generator/graph.py`, `src/taxonomy_generator/routing/should_summarize.py`, `src/taxonomy_generator/routing/should_aggregate_values.py` (new), `main.py` (`STEP_INFO` entry only), `tests/unit_tests/test_routing.py`
- **Approach:**
  1. Extend `should_summarize` to return `Literal["summarize", "get_minibatches", "label_documents"]`: `mode == "test"` → `label_documents`; else existing skip logic (KTD2). Update its docstring to "route after corpus load".
  2. New `should_aggregate_values(state, config)`: `mode == "test"` → `aggregate_new_values`, else `END`.
  3. Register `aggregate_new_values`; map the new `label_documents` branch on the load-corpus conditional edge; replace `label_documents → END` with the aggregate conditional edge.
  4. Add the `aggregate_new_values` entry to `STEP_INFO` in `main.py`.
- **Test scenarios:**
  - `mode=test` → post-load route is `label_documents`; `train` + `skip_summarization=false` → `summarize`; `train` + skip → `get_minibatches`.
  - `should_aggregate_values` routes by mode in both directions.
  - Graph compiles; both terminal paths exist (train: `select_dimensions → label_documents → END`; test: `load_corpus → label_documents → aggregate_new_values → END`).
  - Covers AE1. A compiled-graph or routing-level check that seeded state (non-empty `clusters`) routes open-coded batches to `update_taxonomy`.
- **Verification:** `make test` passes; `python -c "from taxonomy_generator.graph import graph"` succeeds.

### U6. CLI integration

- **Goal:** The operator drives everything from `main.py`: mode, seed, feedback, and delta output.
- **Requirements:** R3, R8, R9 (display half), R4 (wiring half)
- **Dependencies:** U1–U5.
- **Files:** `main.py`, `tests/unit_tests/test_cli.py`
- **Approach:**
  1. Add flags: `--mode {train,test}`, `--taxonomy PATH`, and a mutually exclusive `--feedback TEXT` / `--feedback-file PATH` group.
  2. Resolve feedback with precedence CLI flag > `config.yaml` (`feedback.text` / `feedback.file`); build `UserFeedback(decision="modify", ...)` and pass it via `invoke_input["user_feedback"]`; pass `mode` and `taxonomy_input` via `configurable`.
  3. Startup panel shows mode and, when seeded, the seed's taxonomy name and dimension count.
  4. Stream accumulation: capture `delta_summary` like `saturation_history`; in test mode render a delta panel (new-values table + fallback doc list) and write `delta_summary` into the saved taxonomy JSON (KTD6).
  5. Adjust the taxonomy-rationale iteration labels for test mode ("Seed", "Aggregation" instead of the train-mode tail labels).
  6. Extend the usage docstring with train-from-seed and test-mode examples.
- **Test scenarios:**
  - `parse_args` accepts all new flags; `--feedback` with `--feedback-file` is rejected.
  - Feedback resolution precedence: CLI text > CLI file > config text > config file > none (pure function over args + settings).
  - Delta panel renders new values and fallback docs (captured rich console).
  - Taxonomy serialization includes `delta_summary` when present and omits it otherwise.
  - Covers AE4. Resolved config feedback lands in `invoke_input["user_feedback"]` with `decision="modify"`.
  - Covers AE5. With no new flags, `invoke_input` and `configurable` match today's shapes.
- **Verification:** `make test` and `make lint` pass; `python main.py --help` shows the new flags.

---

## Verification Contract

| Check | Command | Applies to |
|---|---|---|
| Unit tests (mocked LLMs, no network) | `make test` | U1–U6 |
| Lint + types | `make lint` | All units |
| Graph imports and compiles | `python -c "from taxonomy_generator.graph import graph"` | U5 |
| CLI surface | `python main.py --help` | U6 |
| Fresh-run regression (network) | `python main.py --corpus examples/product_reviews.json --quiet --output output/` | R2 / AE5 |
| Seeded train smoke (network) | `python main.py --corpus examples/pharmacy-food/pharmacy_food_architecture_decisions.json --config examples/pharmacy-food/pharmacy_food_config.yaml --taxonomy examples/pharmacy-food/pharmacy-food_taxonomy_20260817_112807.json --quiet --output output/` | AE1 |
| Test-mode smoke (network) | Same as above plus `--mode test` | AE2, AE3, R9, R10 |

Network smoke runs are conditional validation (they need provider keys); the mocked unit suite is the required gate.

---

## Definition of Done

- All units U1–U6 implemented; `make test` and `make lint` pass.
- A fresh run with no taxonomy input produces output identical in shape and behavior to today (R2, AE5).
- A seeded train run's first axial pass is `update_taxonomy` (AE1), and feedback from flag/file/config reaches update and review prompts (AE4).
- A test run freezes dimensions, appends only deduplicated new values with supporting evidence, routes no-fit docs to the fallback bucket, and shows/saves the delta summary (AE2, AE3, R9, R10).
- `config.yaml`, `settings.py`, `configuration.py`, and `SETTINGS.md` all carry the new settings; `pyproject.toml` and `requirements.txt` both carry the new dev dependencies.
- No experimental or dead-end code from abandoned approaches remains in the diff.