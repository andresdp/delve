---
title: Taxonomy Evaluation Suite - Plan
type: feat
date: 2026-08-20
topic: taxonomy-evaluation-suite
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-brainstorm
execution: code
---

# Taxonomy Evaluation Suite - Plan

## Goal Capsule

- **Objective:** Score generated taxonomies against the pipeline's existing quality criteria as LLM-as-judge metrics (deepeval), compare multiple saved taxonomies for run-to-run consistency, and surface the results as terminal scoreboards, saved JSON artifacts, and a section of the grounded-theory report — through both an observe-only in-graph evaluation and a standalone evaluation of any saved final taxonomy.
- **Product authority:** This plan owns NEW_IDEAS items 4 (multi-run consistency) and 5 (LLM-as-judge criteria scoreboard with standalone mode). The review-loop return arc (item 6), design-space solution sampling (item 7), and orchestrated repeated runs are not active scope.
- **Open blockers:** None.
- **Stop conditions:** Ship when both surfaces produce scoreboards and consistency reports per the Requirements; do not expand into gating, return arcs, or run orchestration.

---

## Product Contract

**Product Contract preservation:** Product Contract unchanged — enrichment added Planning Contract, Implementation Units, Verification Contract, and Definition of Done below.

### Summary

A taxonomy evaluation suite built on deepeval: quality criteria from the existing review prompt become judge metrics producing a per-criterion scoreboard (score + rationale), and a consistency mode compares 2+ saved taxonomy JSONs (recurring vs one-off dimensions). It runs observe-only inside the graph (train runs score their final taxonomy; test runs score the frozen taxonomy against the new corpus) and standalone against any saved taxonomy, with optional corpus; results reach the terminal, a saved JSON artifact, and the grounded-theory report.

### Problem Frame

The pipeline's quality criteria — orthogonality, clarity, completeness, use-case alignment, no catch-alls, axis-vs-value, coverage — exist only as prose inside the generation and review prompts, consulted once during a run and then lost. There is no way to measure how good a produced taxonomy actually is, no way to compare it against another run's taxonomy on the same corpus, and no quality signal in the shareable report. Every prior plan in this area parked the evaluation suite as "later"; the pieces it depends on (values with supporting evidence, selected dimensions, saved-taxonomy reuse) have all now shipped, which makes the suite the natural next unit — and the calibration data any future quality gate will need.

### Key Decisions

- **deepeval as the evaluation framework** (session-settled: user-directed — chosen over a native structured-output judge suite: battle-tested scoring templates and aggregation preferred over zero-dependency consistency with the repo's own chain patterns). Governs R1, R2.
- **Two-tier criteria: structure-only floor, data-grounded when documents are available** (session-settled: user-approved — chosen over taxonomy-only and corpus-always: a lone saved JSON still earns a meaningful scoreboard while coverage gets judged when a corpus is at hand). Governs R2, R4.
- **Consistency is post-hoc comparison of saved taxonomies; repeated-run orchestration is deferred** (session-settled: user-approved — chosen over an orchestrated `--runs N` mode: the comparison semantics are the core; orchestration is a thin wrapper once they are proven). Governs R5.
- **In-graph evaluation is observe-only and covers both run modes** (session-settled: user-approved — chosen over gate/feedback integration and over train-only evaluation: train scores its final taxonomy, test scores the frozen taxonomy against the new corpus as a drift signal, and termination stays deterministic while scorecards accumulate for later threshold calibration). Governs R6.
- **Consistency matching is a hybrid: embedding-based dimension alignment with judge adjudication, exposed as custom deepeval metrics** (session-settled: user-approved — accepted under the deepeval banner since aligning dimensions across taxonomies is a matching problem, not a pure judging problem). Governs R5.
- **Scoreboards reach three surfaces: terminal, saved JSON, and a report section** (session-settled: user-approved — chosen over terminal-only and terminal+JSON: the report is the durable shareable artifact and gains quality signals at no extra LLM cost). Governs R7, R8, R9.

### Requirements

**Judge scoreboard**

- R1. The suite scores a taxonomy against criteria derived from the existing review-criteria table (orthogonality, clarity, completeness, use-case alignment, no catch-alls, axis-vs-value, dimensional coverage), implemented as LLM-as-judge metrics using deepeval.
- R2. Structural criteria always run; data-grounded criteria run only when documents are available and are visibly marked "not evaluated" otherwise.
- R3. Every scored criterion reports a score plus the judge's rationale, sufficient to trace the verdict back to taxonomy content.

**Standalone evaluation**

- R4. A standalone mode evaluates any saved final taxonomy JSON (mirroring the existing on-demand report/visualization pattern), optionally paired with a corpus to activate data-grounded criteria.

**Consistency comparison**

- R5. A consistency mode takes two or more saved taxonomy JSONs from the same corpus and produces a comparison identifying recurring dimensions, one-off dimensions, and an overall agreement signal.

**In-graph evaluation**

- R6. Runs evaluate their taxonomy during the run, observe-only: train mode scores its final (post-selection) taxonomy, and test mode scores the frozen seeded taxonomy against the new corpus as a drift signal. Evaluation output never routes the graph, alters termination, or modifies the taxonomy.
- R7. An evaluation failure (judge error, no model access) never fails the enclosing pipeline run or report generation; the scoreboard degrades to a clearly marked unavailable state.

**Outputs**

- R8. Both surfaces render the scoreboard in the terminal and save it as a timestamped JSON artifact following the existing output-file conventions.
- R9. The grounded-theory report gains an evaluation section rendering stored scores verbatim (no additional LLM calls), included whenever evaluation results exist for the rendered taxonomy and omitted otherwise.

### Actors

- **Pipeline operator** — runs the pipeline or the standalone evaluation; triggers scoring and consumes the terminal scoreboard.
- **Report reader** — a collaborator who did not run the pipeline; reads quality signals and consistency findings in the report.

### Key Flows

- F1. Standalone evaluation
  - **Trigger:** Operator invokes standalone evaluation on a saved taxonomy JSON, optionally with a corpus.
  - **Steps:** Taxonomy (and corpus, if given) loaded → structural criteria judged → data-grounded criteria judged or marked not-evaluated → scoreboard rendered, saved, and available for the report.
  - **Covers:** R1, R2, R3, R4, R8.
- F2. Consistency comparison
  - **Trigger:** Operator invokes consistency mode on 2+ saved taxonomy JSONs.
  - **Steps:** Dimensions embedded and aligned across taxonomies → borderline alignments adjudicated → recurring/one-off dimensions and agreement signal reported like a scoreboard.
  - **Covers:** R5, R3, R8.
- F3. In-graph evaluation (train run)
  - **Trigger:** A train-mode run reaches its settled final taxonomy.
  - **Steps:** Criteria judged over the final taxonomy (documents available in state) → scoreboard stored in run output → pipeline continues unchanged to labeling.
  - **Covers:** R1, R2, R3, R6, R7, R8.
- F4. In-graph evaluation (test run)
  - **Trigger:** A test-mode run with a seeded taxonomy proceeds to labeling.
  - **Steps:** Frozen taxonomy judged against the new corpus documents → drift scoreboard stored in run output → run continues unchanged through labeling and value aggregation.
  - **Covers:** R2, R3, R6, R7, R8.

### Acceptance Examples

- AE1. **Covers R2, R4.** Given a saved taxonomy JSON with no corpus supplied. When standalone evaluation runs. Then structural criteria are scored and every data-grounded criterion is listed as "not evaluated" rather than omitted.
- AE2. **Covers R4.** Given the same taxonomy plus its corpus. When standalone evaluation runs. Then dimensional coverage is scored with document-grounded rationale.
- AE3. **Covers R5.** Given two saved taxonomies from runs on the same corpus sharing three dimensions and each holding one unique dimension. When consistency mode runs. Then the three recurring dimensions are identified as matches and both one-offs are flagged.
- AE4. **Covers R6, R7.** Given a train run where the judge call fails. When the run completes. Then all standard outputs are produced unchanged and the scoreboard is marked unavailable rather than the run failing.
- AE5. **Covers R9.** Given a report generated for a taxonomy with stored evaluation results. When the report renders. Then the evaluation section shows the stored scores and rationales without invoking any model.
- AE6. **Covers R6.** Given a test-mode run over a new corpus with a seeded taxonomy. When the run completes. Then a scoreboard for the frozen taxonomy against the new corpus is produced alongside the delta summary, and the seeded dimensions are unchanged.

### Success Criteria

- A saved taxonomy can be scored and compared without re-running the pipeline.
- Scoreboard verdicts are explainable: each score carries a rationale a reader can check against the taxonomy itself.
- Scorecards accumulate across runs and corpora, providing the calibration data a future quality gate would need.

<!-- ce-section: work-relationships -->
### How This Work Fits Together

This plan owns the **evaluation suite** (NEW_IDEAS items 4–5). The breakdown below is the current understanding, not a committed roadmap; later plans may revise, split, merge, or discard these areas.

- Review-loop return arc (item 6) — **Depends on** this plan: a bounded review revision loop wants the scoreboard as its stop-condition signal; parked until thresholds are calibrated from real scorecards.
- Orchestrated repeated runs (`--runs N`) — **Depends on** this plan's consistency comparison; a thin execution wrapper once comparison semantics are proven.
- Design-space solution sampling (item 7) — **Can proceed independently of** this plan; consumes the consolidated values both features build on, and could later adopt this suite's judges for consistency/diversity checks on sampled solutions.

### Scope Boundaries

**Deferred for later**

- Orchestrated repeated-run execution (`--runs N`) — comparison engine ships first.
- Gate/feedback integration: thresholds, return arcs, or automated re-review driven by scores (item 6).
- Design-space solution sampling across dimension values (item 7).
- Pass/fail gating of taxonomies by score thresholds — waits for calibration data.
- Using deepeval as the repository's test/CI harness — deepeval is consumed as a metric library for the product surfaces, not introduced as the test framework.

### Dependencies / Assumptions

- deepeval is a new runtime dependency (absent from `pyproject.toml` and `requirements.txt` today); its judge-model wiring must be pointable at the project's configured providers, and evaluation degrades per R7 where a provider cannot serve it.
- The criteria set originates in the review prompt's criteria table (`src/taxonomy_generator/prompts/taxonomy_review.md`); the exact criterion-to-metric mapping is a planning concern.
- Consistency matching assumes the already-configured embedding provider (`models.embedding`); taxonomy JSONs may lack `relations`/`values` keys (older saves) and must degrade like the report renderer does.
- Test mode reaches labeling without dimension selection, so its in-graph evaluation rides alongside labeling (F4) rather than after selection (F3).

### Outstanding Questions

**Deferred to Implementation**

- OQ0 (resolved in planning). Judge model selection is KTD2 (`evaluation.judge_model`, falling back to the main model); scoring scales and aggregation are KTD4 (GEval native 0-1, mean overall); artifact naming and report placement are KTD8/KTD9.
- OQ1. Exact deepeval API pin (`deepeval>=3.x`): confirm at install time that `GEval`, `DeepEvalBaseLLM`, `evaluate`, and `SingleTurnParams` import from the documented modules and that `GEval.measure` works against the LangChain-wrapped judge; adjust imports if the minor version moved them.
- OQ2. Default judge thresholds per criterion: start from the single configured `evaluation.threshold` (0.5); revisit per-criterion thresholds only when real scorecards show a criterion needs one.

### Sources / Research

- `docs/NEW_IDEAS.md` — items 4 and 5 are the origin of this scope; items 1–3 are shipped (reusable taxonomies merged via PR #1, grounded-theory report on main).
- `docs/TAXONOMY_QUALITY_PLAN.md` — Appendix A maps the deferred evaluation criteria (inter-rater reliability, multi-seed selection, label accuracy) this suite begins to operationalize.
- `src/taxonomy_generator/prompts/taxonomy_review.md` — the seven-criteria review table the judge metrics derive from.
- `src/taxonomy_generator/nodes/saturation_checker.py`, `src/taxonomy_generator/nodes/taxonomy_reviewer.py` — the existing critic/actor split; saturation feeds `{feedback}` today, review runs once post-loop.
- `src/taxonomy_generator/graph.py` — current topology, including the test-mode path that skips summarization, minibatching, and dimension selection.
- `main.py`, `src/taxonomy_generator/report_renderer.py` — the standalone `--report`/`--visualize` pattern, output-file conventions, and the report the evaluation section extends.
- `docs/plans/2026-08-17-1725-feat-reusable-taxonomies-plan.md` — parked the evaluation suite as the natural follow-on to test mode.
- `docs/solutions/architecture-patterns/surface-langgraph-node-output-through-state-schema-to-cli-and-report.md` — the four-step recipe (State/OutputState → node return → three-point `main.py` accumulation → report renderer threading) U4/U5 follow for the `evaluation` field.
- `src/taxonomy_generator/nodes/value_consolidator.py`, `src/taxonomy_generator/utils.py` — the embed → normalize → pairwise distance → threshold + borderline-LLM pattern U3 reuses for dimension alignment.
- deepeval G-Eval documentation: https://deepeval.com/docs/metrics-llm-evals — `GEval(name, criteria|evaluation_steps, evaluation_params=[SingleTurnParams...])`, `include_reason`, `threshold`, custom models via `DeepEvalBaseLLM`. Verified against the live docs page.

---

## Planning Contract

### Key Technical Decisions

- KTD1. **deepeval is consumed as an embedded metric library, not a harness.** Criteria run through `GEval` instances invoked via deepeval's programmatic `evaluate()` (or per-metric `measure()`) inside the pipeline and the standalone CLI path; no pytest suite, no `assert_test`, no Confident AI reporting is introduced. Metric instances live in a dedicated `src/taxonomy_generator/evaluation/metrics.py`, mirroring deepeval's own metrics-module best practice. Governs R1, R8.
- KTD2. **Judge wiring uses deepeval's built-in OpenAI integration; no custom adapter.** (session-settled: user-directed — chosen over a `DeepEvalBaseLLM` wrapper over `load_chat_model()`: the built-in OpenAI integration is used directly for OpenAI or OpenAI-compatible models; the wrapper path is documented in `evaluation/judge.py` as a comment for other providers but deliberately not implemented.) `resolve_judge_model()` strips the `openai/` prefix and passes the bare model name to `GEval`; `None`/empty lets GEval use its built-in default; a non-OpenAI provider raises a clear `ValueError` naming the future wrapper path. Anonymous telemetry is always opted out programmatically (`DEEPEVAL_TELEMETRY_OPT_OUT=1` set in `evaluation/judge.py` before any deepeval use) — no user-facing flag. Governs R1, R3; resolves OQ1 (judge model selection).
- KTD3. **One `GEval` per review-criteria row; criteria text adapted from `taxonomy_review.md` into everyday-language judging instructions.** Six structural criteria (orthogonality, clarity, completeness, use-case alignment, no catch-alls, axis-vs-value) judge `(input=use_case, actual_output=formatted taxonomy)`; the data-grounded coverage criterion judges `(input=sampled document contents, actual_output=formatted taxonomy)`. Each uses `evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT]` only — no reference fields the test case does not carry. `include_reason=True` supplies R3's rationale. The taxonomy serialization for judging is name + description + values per dimension (compact JSON, same fields `format_taxonomy()` emits). Governs R1, R2, R3.
- KTD4. **The scoreboard is a plain dict, serialized from metric results.** Shape: `{"criteria": [{"name", "score", "threshold", "passed", "reason", "evaluated"}], "overall": mean score of evaluated criteria, "model": judge name, "unavailable": false}` — data-grounded criteria without documents carry `"evaluated": false` and no score; a judge failure produces `{"unavailable": true, "error": "..."}` with an empty criteria list. `passed` flags come from the configured threshold and are display-only — nothing gates on them (per R6's observe-only contract). Governs R2, R3, R7; resolves OQ2 (scoring scale: GEval's native 0–1).
- KTD5. **Consistency comparison is a deterministic embedding alignment pass plus judge adjudication of borderline pairs — not a `GEval` metric.** Dimensions from each taxonomy are embedded (`models.embedding`, reusing `load_embeddings_model()`), L2-normalized, and greedily aligned across files by pairwise distance; pairs inside the borderline band around `evaluation.consistency_threshold` go to one judge call for same-dimension adjudication (the `value_consolidator.py` two-tier pattern). Output: recurring dimension groups, per-file one-offs, and an agreement score (aligned dimensions / max dimension count) — a plain dict rendered through the same scoreboard display path. `GEval` is unsuitable here because scoring one merged input cannot express per-dimension alignment. Governs R5.
- KTD6. **One observe-only `evaluate_taxonomy` node serves both modes; placement differs by mode.** Train: `select_dimensions → evaluate_taxonomy → label_documents`. Test: `label_documents → evaluate_taxonomy → aggregate_new_values`. The node reads the effective view (train: `selected_clusters[-1]` when present, else `clusters[-1]`; test: `clusters[-1]`, the frozen seed), samples up to `evaluation.max_documents` documents for the coverage criterion, and returns only `{"evaluation": scoreboard, "status": [...]}` — it never writes `clusters`, `selected_clusters`, or routing-relevant state. Wiring: replace `select_dimensions → label_documents` with the two-step path; extend `should_aggregate_values` so test mode routes `label_documents → evaluate_taxonomy`; add a mode-based conditional edge from `evaluate_taxonomy` (`train → label_documents`, `test → aggregate_new_values`). `evaluation.enabled: false` restores today's exact topology via the routing functions (both conditionals fall through to the direct edges). Governs R6, F3, F4.
- KTD7. **`evaluation` state field + CLI surfacing follow the four-step recipe from the repo learning.** `evaluation: Optional[Dict]` on both `OutputState` and `State` (flat dict — verify nesting against the declared type, not the neighboring field); the node returns it flat; `main.py` adds the three accumulation points (local init, `astream` loop guard, conditional `taxonomy_data["evaluation"]`) plus a `STEP_INFO` entry and a rich scoreboard panel modeled on `_display_delta_summary`. Governs R6, R8.
- KTD8. **Standalone mode is `--evaluate TAXONOMY [TAXONOMY ...]`** in the existing mutually-exclusive standalone group (`--visualize`/`--report`): one file runs the scoreboard (with optional `--corpus` activating the coverage tier, per the existing `load_corpus()` reader); two or more files run the consistency comparison (KTD5). Output follows the convention: `{name_prefix}evaluation_{timestamp}.json` in the resolved output dir, plus the terminal panel. `--iteration` selects the view exactly as `_select_clusters_for_visualize` does. Governs R4, R5, R8.
- KTD9. **The report section is deterministic rendering of stored scores.** `render_evaluation(scoreboard)` in `report_renderer.py` emits a `## Evaluation` section (per-criterion score, pass flag, reason; overall; "not evaluated" rows for skipped data-grounded criteria) from the saved scoreboard only — no model calls. It threads through `assemble_report`/`generate_and_write_report` as optional trailing parameters (the `dropped_dimensions` pattern), placed after Discarded Dimensions. The auto-report on `--output` passes the in-run scoreboard; standalone `--report` renders the `evaluation` key stored in the taxonomy JSON when present and omits the section otherwise. Governs R9.
- KTD10. **No test framework is introduced; verification follows current repo practice.** `make lint` (ruff + mypy) plus import checks and manual CLI smoke runs against the checked-in example taxonomies — matching how the grounded-theory-report and reusable-taxonomies features were verified on this repo. Governs the Verification Contract.

### High-Level Technical Design

Mode-dependent wiring for the observe-only node (KTD6) and the scoreboard's three surfaces:

```mermaid
flowchart TB
    subgraph train[Train mode]
        SEL[select_dimensions] --> EV1[evaluate_taxonomy<br/>final view] --> LAB1[label_documents] --> END_T([END])
    end
    subgraph test[Test mode]
        LAB2[label_documents] --> EV2[evaluate_taxonomy<br/>frozen seed vs new corpus] --> AGG[aggregate_new_values] --> END_E([END])
    end
    EV1 -.evaluation dict.- SB[(scoreboard)]
    EV2 -.evaluation dict.- SB
    SB --> TERM[rich scoreboard panel]
    SB --> JSON[evaluation_*.json + taxonomy JSON<br/>'evaluation' key]
    JSON --> REP[report '## Evaluation' section<br/>verbatim, no LLM]
    CLI[--evaluate FILE ...(--corpus)] --> RUNNER[metrics + runner + consistency] --> SB
```

The runner data flow: taxonomy view (and optional document sample) → `LLMTestCase`(s) → `GEval` metrics with the `LangChainJudge` adapter → per-criterion `{score, reason}` → scoreboard dict (KTD4) → the three surfaces. Consistency mode bypasses `GEval` for alignment and uses one judge call for borderline pairs only (KTD5).

### Assumptions

- deepeval's Apache-2.0 package installs cleanly alongside the existing LangChain stack on Python ≥3.9, with anonymous telemetry always opted out programmatically (`DEEPEVAL_TELEMETRY_OPT_OUT=1` set in `evaluation/judge.py`, no user-facing flag) so evaluation runs do not phone home; its transitive dependencies do not conflict with the pinned `langchain*` ranges. Verified at install time (deepeval 4.1.8); a conflict escalates as a blocker, not a silent pin bump.
- `GEval.measure()` against a `DeepEvalBaseLLM` adapter behaves as documented (score in 0–1, `reason` populated with `include_reason=True`); deepeval internals occasionally require `str` model names — `get_model_name` returns the configured model string.
- The judge's context window comfortably holds a formatted taxonomy (≤ `max_num_clusters` dimensions with values) plus a ≤ `evaluation.max_documents` document sample; corpora are small in this repo's usage.
- Older saved taxonomy JSONs without `relations`/`values` keys still produce a judgeable taxonomy (name + description carry the signal), and consistency embedding uses name + description when values are absent.

### Sequencing

U1 → U2 → U3 and U4 (independent of each other once U2 exists) → U5 → U6. U3 needs only U1's settings and embedding utilities; U4 needs U2's runner.

---

## Implementation Units

### U1. Dependency, settings, and judge adapter

- **Goal:** deepeval is installed and configured; the judge adapter makes every configured provider available to deepeval metrics.
- **Requirements:** R1 (framework half)
- **Dependencies:** None.
- **Files:** `pyproject.toml`, `requirements.txt`, `src/taxonomy_generator/settings.py`, `src/taxonomy_generator/configuration.py`, `config.yaml`, `SETTINGS.md`, `src/taxonomy_generator/evaluation/__init__.py`, `src/taxonomy_generator/evaluation/models.py` (new package)
- **Approach:**
  1. Add `deepeval>=3.0.0` to `pyproject.toml` dependencies and `requirements.txt` (repo rule: both files); confirm the installed version exposes `GEval`, `DeepEvalBaseLLM`, `evaluate`, `SingleTurnParams` from the documented modules (OQ1).
  2. Add `EvaluationSettings` to `settings.py`: `enabled: bool = True`, `judge_model: Optional[str] = None`, `threshold: float = 0.5`, `consistency_threshold: float = 0.25`, `consistency_borderline_band: float = 0.08`, `max_documents: int = 20`; wire `Settings.evaluation`, the `config.yaml` `evaluation:` section, `Configuration` fields + `_defaults_from_settings`, and `SETTINGS.md` entries (four-place convention).
  3. In `evaluation/judge.py`, implement `resolve_judge_model()` per KTD2 (updated per user redirect): `openai/<model>` → bare model name for deepeval's built-in OpenAI integration; `None`/empty → GEval's built-in default; any other provider raises `ValueError` naming the documented future-wrapper path (the `DeepEvalBaseLLM` wrapper is deliberately not implemented).
- **Patterns to follow:** `src/taxonomy_generator/utils.py` `load_chat_model()`; `Configuration` field wiring in `configuration.py`.
- **Test scenarios:**
  - `LangChainJudge` constructed with `openai/gpt-5.4-nano` reports that model name and loads a model instance (no network needed for construction).
  - `Configuration.from_runnable_config` resolves `evaluation.enabled`, `threshold`, and `judge_model` from a temporary YAML; unset `judge_model` yields `None` (fallback resolved by callers).
  - Settings round-trip: `load_settings('config.yaml')` exposes the new section with defaults.
- **Verification:** `make lint` passes; `python -c "from taxonomy_generator.evaluation.judge import resolve_judge_model"` succeeds; `python -c "from taxonomy_generator.settings import load_settings; print(load_settings('config.yaml').evaluation)"` prints defaults.

### U2. Metrics module and scoreboard runner

- **Goal:** Seven GEval criteria defined from the review table; a runner turns a taxonomy view (plus optional documents) into the scoreboard dict with R2/R7 semantics.
- **Requirements:** R1, R2, R3, R7
- **Dependencies:** U1.
- **Files:** `src/taxonomy_generator/evaluation/metrics.py`, `src/taxonomy_generator/evaluation/runner.py`
- **Approach:**
  1. `metrics.py` defines `STRUCTURAL_CRITERIA` (six entries: name + criteria text adapted from `src/taxonomy_generator/prompts/taxonomy_review.md`'s Review Criteria table into everyday judging language) and `COVERAGE_CRITERION` (one entry requiring documents). A `build_metrics(judge, threshold)` factory returns `GEval` instances per KTD3 — `evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT]`, `include_reason=True`, `threshold` from configuration.
  2. `runner.py` exports `async run_scoreboard(clusters, documents, configuration) -> dict`: serialize the taxonomy view (name, description, values per dimension — compact JSON); build one `LLMTestCase` per tier (structural: `input=use_case`, `actual_output=taxonomy_json`; coverage: `input="\n".join(sampled doc contents)` capped at `evaluation.max_documents`, `actual_output=taxonomy_json`); run each metric's `a_measure`; assemble the KTD4 dict with `evaluated` flags; when `documents` is empty the coverage row is `"evaluated": false` with no score (R2). Wrap the whole run in a try/except returning `{"unavailable": True, "error": ...}` (R7).
- **Patterns to follow:** deepeval metrics-module practice (skill reference); `saturation_checker.py`'s chain setup and graceful async shape.
- **Test scenarios:**
  - Structural-only run (no documents): six criteria scored, coverage row present with `"evaluated": false`, `overall` = mean of the six (covers AE1 logic).
  - With documents: coverage criterion receives a joined sample capped at `max_documents`; seven scored rows (covers AE2 logic).
  - Judge raising mid-run returns `{"unavailable": True, "error": ...}` and never propagates (covers AE4 logic).
  - Each scored row carries non-empty `reason` and a 0–1 `score`; `passed == (score >= threshold)`.
- **Verification:** `make lint`; a short manual script scoring `examples/campus-bike/campus-bike_taxonomy_20260817_110113.json` (network) prints a well-formed scoreboard with seven rows.

### U3. Consistency comparison

- **Goal:** Two or more saved taxonomies align into recurring/one-off dimensions with an agreement signal.
- **Requirements:** R5, R3 (rationale for adjudicated pairs)
- **Dependencies:** U1 (settings, embedding loader), U2 (judge adapter, scoreboard path).
- **Files:** `src/taxonomy_generator/evaluation/consistency.py`
- **Approach:**
  1. `compare_taxonomies(taxonomies: list[list[dict]], configuration) -> dict`: embed each file's dimension `name + description` (falling back from `name + description + value labels` when values exist) via `load_embeddings_model()`, L2-normalize, and greedily align dimensions across files by ascending pairwise distance below `evaluation.consistency_threshold` (first file's dimensions as anchors; ties resolved by id order for determinism).
  2. Pairs within `consistency_borderline_band` above the threshold go to one judge call (the `LangChainJudge` answering a same-dimension question, structured yes/no) — the `value_consolidator.py` two-tier pattern.
  3. Result dict: `{"files": [...], "agreement": aligned/max_count, "recurring": [{names per file, similarity}], "one_offs": [{file, dimension}]}` — rendered through the same scoreboard display path (KTD5). Embedding loader failure degrades to exact-string name matching with a logged warning, mirroring `value_aggregator`'s fallback.
- **Patterns to follow:** `src/taxonomy_generator/nodes/value_consolidator.py` (embed → normalize → threshold → borderline LLM), `src/taxonomy_generator/utils.py` (`l2_normalize`, `pairwise_euclidean`, `connected_components`).
- **Test scenarios:**
  - Two taxonomies sharing three near-identical dimensions plus one unique each: three recurring groups, two one-offs, agreement 0.75 (3/4) (covers AE3).
  - Borderline pair (mocked distance inside the band) triggers exactly one judge call; its verdict decides the group.
  - Old-format taxonomy without `values` keys aligns on name+description without error.
  - Embedding loader raising falls back to exact-name matching; run completes with a warning.
- **Verification:** `make lint`; manual run comparing the three `examples/campus-bike/campus-bike_taxonomy_*.json` files (network) prints recurring dimensions and an agreement score.

### U4. In-graph evaluate_taxonomy node and wiring

- **Goal:** Both run modes produce an in-run scoreboard, observe-only, with the pipeline's behavior unchanged when disabled.
- **Requirements:** R6, R7, F3, F4
- **Dependencies:** U2 (runner).
- **Files:** `src/taxonomy_generator/nodes/taxonomy_evaluator.py` (new), `src/taxonomy_generator/state.py`, `src/taxonomy_generator/graph.py`, `src/taxonomy_generator/routing/should_aggregate_values.py`, `src/taxonomy_generator/routing/should_continue_after_evaluation.py` (new), `main.py` (`STEP_INFO` entry only)
- **Approach:**
  1. `state.py`: add `evaluation: Optional[Dict]` to `OutputState` and `State` (flat, replace semantics — no reducer; KTD7).
  2. `taxonomy_evaluator.py`: `async evaluate_taxonomy(state, config)` reads mode from configuration; resolves the view per KTD6 (train: `selected_clusters[-1] or clusters[-1]`; test: `clusters[-1]`); samples up to `evaluation.max_documents` documents from state; calls `run_scoreboard`; returns `{"evaluation": scoreboard, "status": [...]}`. When `evaluation.enabled` is false or the resolved view is empty, return `{"evaluation": None, "status": [...]}` so downstream accumulation skips it.
  3. `graph.py`: register the node; replace `select_dimensions → label_documents` with `select_dimensions → evaluate_taxonomy`; make `label_documents`' outgoing conditional (extended `should_aggregate_values`) route test mode to `evaluate_taxonomy`; add `should_continue_after_evaluation` returning `"label_documents"` (train) or `"aggregate_new_values"` (test); when `evaluation.enabled` is false both routing functions return the direct destinations so today's topology is preserved.
  4. `main.py`: add the `evaluate_taxonomy` `STEP_INFO` entry (e.g. `("🎯", "Evaluating taxonomy")`).
- **Patterns to follow:** `nodes/saturation_checker.py` (node shape, config reads, logging); routing functions' mode reads (`should_aggregate_values.py`).
- **Test scenarios:**
  - Train routing: `select_dimensions` → `evaluate_taxonomy` → `label_documents`; test routing: `label_documents` → `evaluate_taxonomy` → `aggregate_new_values` (covers F3/F4 wiring).
  - `evaluation.enabled: false`: routing functions return `label_documents`/`aggregate_new_values` directly — topology identical to today.
  - Node with a judge failure returns `evaluation: {"unavailable": True}` and the graph still completes to labeling (covers AE4).
  - Node output never contains `clusters`, `selected_clusters`, or `documents` keys (observe-only invariant).
  - Graph compiles: `python -c "from taxonomy_generator.graph import graph"`.
- **Verification:** `make lint`; graph import compiles; a full train run with `--output` (network) shows the evaluation step between selection and labeling and completes normally.

### U5. CLI surfacing, JSON artifact, and report section

- **Goal:** In-run scoreboards reach the terminal, the saved taxonomy JSON, and the grounded-theory report.
- **Requirements:** R8, R9
- **Dependencies:** U4.
- **Files:** `main.py`, `src/taxonomy_generator/report_renderer.py`
- **Approach:**
  1. `main.py` `run()`: the three accumulation points for `evaluation` (local init; `if "evaluation" in node_output:` in the `astream` loop; conditional `taxonomy_data["evaluation"] = evaluation` when not `None` and not `unavailable`-empty) — KTD7 and the repo learning's checklist.
  2. `_display_scoreboard(scoreboard, configuration)`: rich panel modeled on `_display_delta_summary` — a criteria table (name, score, pass marker, short reason) with "not evaluated" rows and the overall score; an unavailable scoreboard renders a one-line notice instead.
  3. `report_renderer.py`: `render_evaluation(scoreboard) -> str` emitting the deterministic `## Evaluation` section per KTD9; thread `evaluation` through `assemble_report`/`generate_and_write_report` as optional trailing parameters, appended after Discarded Dimensions only when non-empty; the auto-report path passes the in-run scoreboard, and standalone `--report` reads the stored `evaluation` key from the taxonomy JSON when present (R9's omission-otherwise).
- **Patterns to follow:** `docs/solutions/architecture-patterns/surface-langgraph-node-output-through-state-schema-to-cli-and-report.md` (the exact four-step recipe); `_display_delta_summary`; `render_discarded_dimensions` + its `assemble_report` threading.
- **Test scenarios:**
  - A run with a populated scoreboard saves `evaluation` inside the taxonomy JSON and renders the report section (covers AE5's in-run half).
  - `--report` on a saved taxonomy JSON containing `evaluation` renders the section verbatim with no model calls; the same file without the key omits the section (covers AE5).
  - An unavailable scoreboard: run completes, panel shows the notice, taxonomy JSON omits `evaluation`, report omits the section.
  - "not evaluated" rows render as such in both the panel and the report section (R2 visibility).
- **Verification:** `make lint`; a network run with `--output` produces the panel, the `evaluation` key in the saved taxonomy JSON, and the report section.

### U6. Standalone --evaluate mode

- **Goal:** Any saved taxonomy (or set of them) is scoreable/comparable without running the pipeline.
- **Requirements:** R4, R5, R8
- **Dependencies:** U2, U3, U5 (display + save helpers).
- **Files:** `main.py`, `README.md` (usage), `docs/EXAMPLES.md` (a short section)
- **Approach:**
  1. Add `--evaluate` (`nargs="+"`) to the mutually-exclusive standalone group with `--visualize`/`--report`; `--corpus` becomes meaningful alongside a single `--evaluate` file (reuse `load_corpus()`; ignored for multi-file consistency mode with a notice).
  2. `_run_evaluate(args)` mirrors `_run_report`: `init_settings(args.config)`; one file → resolve the view via the shared `_select_clusters_for_visualize` (honoring `--iteration`), load optional corpus, await `run_scoreboard`; multiple files → load each and call `compare_taxonomies`. Display via the shared panel, then write `{name_prefix}evaluation_{timestamp}.json` to the resolved output dir (`resolve_output_dir`, `--output` override) and print the path.
  3. Document the new flag in `README.md` and add a compact example to `docs/EXAMPLES.md` using the checked-in campus-bike taxonomies.
- **Patterns to follow:** `_run_report` (uniform standalone mode: settings-only init, view resolution, output-dir handling, path confirmation), `--visualize` mutual-exclusion wiring.
- **Test scenarios:**
  - Covers AE1. `--evaluate <taxonomy.json>` with no corpus: scoreboard with "not evaluated" coverage; JSON artifact written; command exits 0.
  - Covers AE2. `--evaluate <taxonomy.json> --corpus <corpus.json>`: coverage scored with document-grounded rationale.
  - Covers AE3. `--evaluate <tax1.json> <tax2.json> <tax3.json>`: consistency report with recurring/one-off dimensions and agreement; one JSON artifact.
  - `--evaluate` combined with `--visualize` or `--report` is rejected by argparse.
  - `--evaluate <missing.json>` fails with a clear path-naming error.
- **Verification:** `make lint`; `python main.py --help` shows the flag; the three network smoke commands from the Verification Contract run against `examples/campus-bike/` and `examples/product_reviews.json`.

---

## Verification Contract

| Check | Command | Applies to |
|---|---|---|
| Lint + types | `make lint` | All units |
| Package imports | `python -c "from taxonomy_generator.evaluation.models import LangChainJudge; from taxonomy_generator.evaluation.runner import run_scoreboard; from taxonomy_generator.evaluation.consistency import compare_taxonomies"` | U1–U3 |
| Graph compiles | `python -c "from taxonomy_generator.graph import graph"` | U4 |
| CLI surface | `python main.py --help` | U6 |
| Standalone scoreboard, no corpus (network) | `python main.py --evaluate examples/campus-bike/campus-bike_taxonomy_20260817_110113.json --output output/` | U2, U6; AE1 |
| Standalone scoreboard with corpus (network) | `python main.py --evaluate examples/campus-bike/campus-bike_taxonomy_20260817_110113.json --corpus examples/campus-bike/campus_bike_architecture_decisions.json --config examples/campus-bike/campus_bike_config.yaml --output output/` | U2, U6; AE2 |
| Consistency across runs (network) | `python main.py --evaluate examples/campus-bike/campus-bike_taxonomy_20260817_101247.json examples/campus-bike/campus-bike_taxonomy_20260817_104940.json examples/campus-bike/campus-bike_taxonomy_20260817_110113.json --output output/` | U3, U6; AE3 |
| In-graph train evaluation (network) | `python main.py --corpus examples/product_reviews.json --output output/` | U4, U5; F3 |
| Report renders stored scores (deterministic) | `python main.py --report <taxonomy JSON saved by the in-graph run> --output output/` | U5; AE5 |
| Disabled path unchanged (network) | A run with `evaluation.enabled: false` produces output identical in shape to today (no evaluation step, no `evaluation` key) | U4 |

Network runs are conditional validation (they need provider keys); `make lint` and the import/compile checks are the required offline gate, per KTD10.

---

## Definition of Done

- All units U1–U6 implemented; `make lint` passes with no new findings.
- A fresh train run scores its final taxonomy between selection and labeling, saves the scoreboard in the taxonomy JSON and as part of the standard outputs, displays the panel, and includes the report section (F3, R6, R8, R9).
- A test run scores the frozen seed against the new corpus alongside labeling and changes no seeded dimensions (F4, AE6).
- Standalone `--evaluate` scores one taxonomy (with and without `--corpus`) and compares 2+ taxonomies, each writing an `evaluation_*.json` artifact (AE1–AE3, R4, R5).
- Judge failures degrade to the unavailable scoreboard everywhere and never fail a run or report (R7, AE4).
- `evaluation.enabled: false` restores today's behavior exactly; with deepeval-related imports intact, a disabled or keyless environment still completes standard runs.
- `config.yaml`, `settings.py`, `configuration.py`, and `SETTINGS.md` all carry the new `evaluation` settings; `pyproject.toml` and `requirements.txt` both carry `deepeval`.
- No experimental or dead-end code from abandoned approaches remains in the diff.