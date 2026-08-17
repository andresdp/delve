# Taxonomy Quality & Design-Space Enhancement Plan

> Status: **implemented** (§9 build order 1–8). Open items remain only where the plan flagged empirical tuning (§10 thresholds, embedding model choice). Companion to [DESIGN.md](DESIGN.md).

## 1. Motivation

Delve currently generates a taxonomy (TnT-LLM-style: summarize → generate → iteratively update → review → label) but has no mechanism to check whether that taxonomy is actually a well-formed **design space** — orthogonal dimensions, each with real values/decisions — or whether it would hold up on new data (relevance/enduringness). There is also no automated feedback loop: the graph already has a `{feedback}` slot and a `UserFeedback` schema, but today only a human can populate it.

This plan adds automated checks grounded in two papers already in `paper/`, wires their output back into the existing feedback mechanism as reflection steps, and borrows structure from grounded theory (GT) coding to make the intermediate artifacts (open codes, values, relationships) explicit instead of collapsed into a single LLM judgment call.

**Primary sources:**
- Wan et al., *TnT-LLM: Text Mining at Scale with Large Language Models* (`paper/TNT-LLM-2403.12173v1.pdf`) — the framework this repo already implements; its §4 evaluation suite (coverage, label accuracy, relevance, inter-rater reliability) and §3.1 mixture-model/SGD framing of the minibatch loop.
- Shaw, *Design Space* (`paper/ShawDesignSpace-a.pdf`) — dimensions vs. values, orthogonality, dependency between decisions, hierarchical vs. instance-oriented representation, composite validation against real designs.
- Grounded theory: delvetool.com's open/axial/selective coding primer; [`llm_assisted_gt`](https://github.com/MingfengHong/llm_assisted_gt) (a 5-stage LLM pipeline with an explicit saturation test); [`interpretive-orchestration`](https://github.com/linxule/interpretive-orchestration) (human-in-the-loop "sandwich" architecture, multi-model triangulation).

**Explicitly out of scope for this build** (discussed, parked for later): a BERTopic-style embedding-clustering baseline for head-to-head comparison; the "core category" / hub-and-spoke restructuring version of selective coding (this plan uses the narrower "select relevant subset of dimensions" interpretation instead); a front-loaded mandatory human solo-coding stage.

## 2. Design principles carried through the whole plan

1. **Context is `use_case`, reused everywhere.** Every new prompt (open coding, relation typing, saturation check, dimension selection) takes the existing `use_case` string — no new context field.
2. **Cheap/deterministic checks gate expensive LLM calls, not replace them.** Embedding-distance filters find candidates; LLM adjudication only runs on the ambiguous cases. This pattern is applied symmetrically at the dimension level (orthogonality) and the value level (consolidation).
3. **Automated critique reuses the existing feedback plumbing.** `UserFeedback`/`{feedback}` generalizes to accept critic-generated text, not only human-authored text.
4. **Nothing is silently deleted.** Dimensions or values that fail a check are flagged/dropped-with-rationale and kept inspectable, not removed outright.

## 3. Revised pipeline

```
load_corpus → summarize → get_minibatches
   → open_code_minibatch (NEW)
   → generate_taxonomy (axial coding, MODIFIED: consumes open codes, drafts relations + values)
   → [ update_taxonomy (MODIFIED, same) ⇄ check_saturation (NEW) ]   loop, routed by should_review (MODIFIED)
   → review_taxonomy (existing)
   → consolidate_values (NEW: embedding-distance merge of draft values, LLM for borderline cases)
   → select_dimensions (NEW: selective coding as use_case-relevance filtering)
   → label_documents (MODIFIED: emits category + value_id)

Optional, invoked from generate_taxonomy / update_taxonomy / review_taxonomy / consolidate_values:
   → render_taxonomy_pca (NEW utility, per-iteration chart export via erdogant/pca)
```

## 4. Schema changes (`schemas.py`)

| Type | Status | Fields | Purpose |
|---|---|---|---|
| `OpenCode` | new | `doc_id`, `label`, `rationale` | Fine-grained per-document concept/decision label — the raw material axial coding organizes, instead of clustering raw summaries directly |
| `Relation` | new | `target_id`, `type: Literal["precondition","consequence","co_occurring","constrains"]`, `rationale` | Typed link between two dimensions (GT's paradigm model), replacing "flag possible overlap" with an explicit relationship |
| `Cluster` | modified | + `relations: list[Relation] = []`, + `values: list[Value] = []` | Dimensions carry both their relationships to other dimensions and their consolidated value set |
| `Value` | new | `id`, `dimension_id`, `label`, `description`, `supporting_doc_ids: list[str]` | A consolidated decision/value within one dimension — the actual "point on the axis" |
| `SaturationCheckOutput` | new | `is_saturated: bool`, `uncovered_concepts: list[str]`, `rationale` | Per-minibatch verdict on whether new open codes are subsumed by existing dimensions |
| `SelectionOutput` | new | `selected_ids: list[str]`, `dropped: list[{id, rationale}]`, `rationale` | Which dimensions are relevant to `use_case`, and why the rest were dropped |
| `LabelOutput` | modified | + `value_id: Optional[str]` | Two-level labeling: which dimension, and which specific decision within it |
| `Doc` | modified | + `value` (mirrors existing `category`) | Carries the assigned value alongside the assigned dimension |
| `UserFeedback` | modified | generalize `feedback` producer to include automated critics, not only humans | Lets check outputs (#saturation, #orthogonality, #relevance) flow into the same `{feedback}` prompt slot |

## 5. Node-by-node plan

| Node | Status | Purpose | Context injection |
|---|---|---|---|
| `open_code_minibatch` | new | Per document in the minibatch, extract fine-grained concept/decision labels before any grouping | `{use_case}` scopes extraction to the stated design space, not generic entity extraction |
| `generate_taxonomy` / `update_taxonomy` | modified | Input becomes accumulated `open_codes` instead of raw summaries; output now includes `relations` and draft `values` per dimension | `{use_case}` bound via `.partial()` as today; relation-typing instructions require relations to be judged against the use case, not incidental textual co-occurrence |
| `check_saturation` | new, runs after each `update_taxonomy` pass | Compares the current minibatch's open codes against the existing taxonomy; sets `is_saturated` | `{use_case}` included so "uncovered" means uncovered *relative to the design space's goals* |
| `should_review` | modified (routing only) | Routes to `review_taxonomy` once `saturation_streak >= threshold` **or** `num_revisions >= num_minibatches`, whichever comes first; if minibatches exhaust without ever saturating, proceeds anyway but records `saturated: false` | — |
| `review_taxonomy` | unchanged | Final polish pass | already has `{use_case}` |
| `consolidate_values` | new | Embeds draft values within each dimension, merges near-duplicates by distance threshold, LLM-adjudicates borderline pairs | `{use_case}` used only in the LLM-adjudication prompt for borderline merges |
| `select_dimensions` | new | Ranks/filters the reviewed dimension set to the subset relevant to `use_case`; drops are kept, marked, not deleted | `{use_case}` is the entire basis for this step |
| `label_documents` | modified | Emits `category` (dimension) + `value_id` (specific decision) instead of just `category` | unchanged prompt context |
| `render_taxonomy_pca` | new utility (not a graph node) | See §7 | n/a |

**State additions:** `open_codes` (accumulator, mirrors `clusters`), `saturation_history` + `saturation_streak`, `selected_clusters` (kept distinct from the full reviewed `clusters[-1]` so both full and filtered taxonomies stay inspectable).

## 6. Value consolidation algorithm

1. Embed each draft value's `label + description` (or pooled open-code labels behind it) using the project's existing multi-provider LLM setup's embedding wrapper.
2. **L2-normalize** the vectors before any distance computation. For normalized vectors, Euclidean distance and cosine similarity are monotonically related (`euclidean² = 2(1 − cosine_sim)`), so normalizing once keeps "distance" consistent between the merge step and the visualization step (§7) — if one used raw cosine similarity and the other unnormalized Euclidean PCA distance, the two views could silently disagree.
3. Compute pairwise distance **within each dimension only** — a value only competes for consolidation with other values on the same axis, never across dimensions.
4. **Threshold merge**: any pair below `epsilon` is treated as the same decision, resolved via union-find/connected-components over the distance graph (deterministic, no LLM cost).
5. **Borderline pairs** (distance just above `epsilon`) go to an LLM adjudication call: "are these the same decision or genuinely different?" — mirrors the two-tier pattern used for dimension-level orthogonality.
6. **Canonical label** per merged group: nearest-to-centroid value, or an LLM synthesis call (one call per surviving value, not per open code).

## 7. Taxonomy visualization (PCA, optionally per iteration)

**Library:** [`erdogant/pca`](https://github.com/erdogant/pca) — takes a numeric matrix (rows = values, columns = embedding dimensions), returns 2D/3D coordinates plus explained variance, and includes outlier detection (Hotelling's T²/SPE) as a bonus signal for a value that sits suspiciously isolated within its dimension (the complement of the merge check, which catches values that are too close).

**Per-iteration generation (this turn's addition):** `render_taxonomy_pca` is a shared utility, not a single graph node, because "iteration" spans multiple different node types across the loop. It is called, optionally, from:
- `generate_taxonomy` (initial draft values)
- each `update_taxonomy` pass (evolving draft values)
- `review_taxonomy` (post-polish draft values)
- `consolidate_values` (final, merged values — the version that should visually show near-duplicates snapping together relative to earlier iterations)

Each call renders one chart and writes one file, named to capture the run and the iteration, e.g. `taxonomy_pca_<run_name>_<stage>_<iter_idx>.png` (`stage` ∈ `generate|update|review|consolidate`). Controlled entirely by config (§8) so it's off by default and doesn't add latency/cost to normal runs.

**What gets plotted:** points = values, colored by dimension; run once globally (cross-dimension sanity check on separation) and optionally once per dimension (zoomed view for reviewing a specific merge decision).

**Caveats to build in, not bolt on later:**
- Report explained variance ratio next to every chart. If 2–3 components capture a low share of total variance, the plot is a weak proxy for true distance and should be visibly labeled as such.
- **Merge decisions are never made from the projected 2D/3D coordinates** — only from the full-dimensional distance computed in §6 step 3. PCA is a lossy linear projection; two points can look close in projection while being farther apart in the full embedding space, or vice versa if the separating variance sits on a discarded component. The chart is a debugging/explanation view of a merge that already happened deterministically, not the source of that decision.
- Confirm the exact save/export mechanism (`pca` library's own plot methods vs. building a matplotlib figure from its returned coordinates for full control over per-iteration filenames) during implementation — not fully pinned down yet.

## 8. Configuration additions (`settings.py` / `config.yaml`)

| Key | Purpose |
|---|---|
| `taxonomy.saturation_streak_threshold` | Consecutive saturated minibatches required to stop early |
| `taxonomy.value_merge_distance_threshold` | Embedding-distance cutoff (`epsilon`) for automatic value consolidation |
| `taxonomy.value_merge_borderline_band` | Distance band above `epsilon` routed to LLM adjudication instead of auto-merge or auto-reject |
| `visualization.enabled` | Master on/off switch (default `false`) |
| `visualization.every_iteration` | If `false`, only render the final (post-`consolidate_values`) chart; if `true`, render at every stage listed in §7 |
| `visualization.dimensions` | `2` or `3` |
| `visualization.output_dir` | Where chart files are written (defaults alongside `--output`) |

## 9. Build order

Later pieces depend on earlier ones; recommended sequence:

1. **Schema additions** (`schemas.py`) — no behavior change, just types (§4).
2. **Saturation-as-stopping-condition** — wraps the existing loop, ships independently, immediately useful (§5 `check_saturation` / `should_review`).
3. **Open coding sub-step** — new node, changes what axial coding consumes (§5 `open_code_minibatch`).
4. **Relationship-typed axial coding** — modify generate/update prompts + `Cluster.relations`, now that open codes exist as grounding (§5).
5. **Value consolidation** — `consolidate_values` node, embedding + threshold merge, LLM for borderline cases (§6).
6. **Selective coding / `select_dimensions`** — depends on the reviewed, value-consolidated taxonomy existing (§5).
7. **Two-level labeling** — extend `label_documents`/`LabelOutput`/`Doc` with `value_id` (§4, §5).
8. **PCA visualization utility** — `render_taxonomy_pca`, wired into steps 2–6 behind the `visualization.enabled` flag (§7).

## 10. Decisions already made / open items

- **Decided:** reuse `use_case` as the sole context carrier; no new `context`/`system_description` field.
- **Decided:** selective coding = filter the dimension set for use-case relevance, not restructure into a hub-and-spoke "core category" hierarchy.
- **Flagged, not yet decided:** exact values for `value_merge_distance_threshold` and `saturation_streak_threshold` — these will need empirical tuning against the example corpora (`examples/das-p1-2023`, `examples/campus-bike`) rather than being guessed upfront.
- **Flagged, not yet decided:** embedding model/provider for the consolidation and visualization steps (reuse an existing LLM provider's embedding endpoint vs. a lighter local model) — a cost/quality tradeoff to settle during implementation.

## Appendix A: Full checklist of quality criteria (source-mapped)

From TNT-LLM: (1) Taxonomy Coverage, (2) Label Accuracy (pairwise judge), (3) Relevance to Use-Case Instruction, (4) Inter-rater/inter-judge reliability, (5) Stochastic-optimization convergence diagnostic, (6) Multi-seed trial selection, (7) Downstream classification accuracy vs. human gold.

From Shaw: (8) Orthogonality/axis-independence, (9) Axis-vs-value detector, (10) Conditional relevance/dependency structure, (11) Value-set completeness per dimension, (12) Composite cross-instance/held-out validation, (13) Representation-form/imbalance check.

This build directly operationalizes #5 (as saturation, §5/§9 step 2), #8/#9 (as the dimension-orthogonality checks feeding relation-typing, §5/§9 step 4), #10 (as `Relation` types, §4), #11 (as value consolidation, §6), and #3 (as `select_dimensions`, §5/§9 step 6). #1, #2, #4, #6, #7, #12, #13 remain candidates for a later evaluation-suite pass, not part of this build.

## Appendix B: Grounded theory phase mapping

| GT concept | Where it lands in this plan |
|---|---|
| Open coding | `open_code_minibatch` (§5) |
| Axial coding + paradigm model | `generate_taxonomy`/`update_taxonomy` drafting `relations` and `values` (§5) |
| Constant comparison | Value consolidation's per-candidate distance check against existing values (§6) |
| Theoretical saturation | `check_saturation` / modified `should_review` (§5) |
| Selective coding (core category) | Deliberately narrowed to relevance filtering — `select_dimensions` (§5) |
| Memoing | Already-existing `explanations[]` accumulator; not extended in this build, noted as a future readability improvement |
| Human solo-coding / multi-model triangulation | Parked (§1, out of scope) |
