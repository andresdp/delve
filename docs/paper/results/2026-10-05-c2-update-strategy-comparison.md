# C2 update-strategy comparison, with a C1 check (preliminary, 2026-10-05)

Preliminary results of comparing three ways the pipeline updates the taxonomy during axial coding
(`taxonomy.edit_mode`), on case C2 (monitoring deployed RL systems). **One run per strategy; the judge is
not independent of the generator.** These are directions, not reportable results.

---

## 1. What is compared with what

Each generated taxonomy is scored against the experts' design-decision model of the study (the C2 ground
truth, `benchmark/c2-rl-monitoring/gt/`).

| Generated taxonomy (DelveDSpace) | | Expert model (ground truth) |
|---|---|---|
| **Dimension**: one design question | vs. | **Decision**: one expert design decision (C2: 7) |
| **Value**: one alternative answer under a dimension | vs. | **Option**: one alternative under a decision (C2: 57 in the paper view, 62 in the model view) |

- Only values with status *accepted* or *rejected* (candidate decisions) are compared; *outcome* values are
  left out.
- **Views:** the *paper view* is what the published paper reports; the *model view* is the authors' full
  design model, which includes a few options the paper omits.
- **Values vs. options:** embeddings propose candidate pairs; a matching LLM labels each pair *same*,
  *broader*, *narrower*, *related* or *different*. A **hit** is *same*, *broader* or *narrower*.
  - **Precision:** system values that hit at least one option ÷ system values compared.
  - **Recall:** options hit by at least one system value ÷ options.
  - **Jaccard:** pairs in a one-to-one matching of hits ÷ size of the union of both sides. Unlike precision
    and recall, it penalizes redundancy (many values for one option, or one value for many options).
- **Dimensions vs. decisions:** derived from the value–option hits. A dimension and a decision are paired
  when enough of their values and options match each other (share ≥ 0.25). **Strict** alignment pairs each
  dimension with at most one decision and vice versa (one-to-one); **lenient** alignment also accepts splits
  and merges. Jaccard is computed on the strict alignment.

Frame, thresholds and judge are fixed in `benchmark/README.md` ("Evaluation frame").

---

## 2. The three update strategies

All three are selected in the YAML settings, per run:

```yaml
taxonomy:
  edit_mode: "rewrite"      # rewrite | rewrite_restore | tools
  edit_max_steps: 12        # tools mode only: maximum model turns per update or review
```

They apply to the two nodes that change the taxonomy during and after the loop: `update_taxonomy` (one call
per minibatch of open codes) and `review_taxonomy` (the final revision). The first draft
(`generate_taxonomy`) and everything after the review (consolidation, evidence linking, selection,
labeling) are the same in all three modes.

### `rewrite` (default; the original pipeline)

- **How it works:** in each update the model receives the whole current taxonomy (without document ids) and
  the new batch's open codes, and returns the **whole updated taxonomy** as structured output. The returned
  taxonomy replaces the previous one; evidence is carried over for values whose label survives.
- **Pros:**
  - Simple; one model call per update.
  - The model can restructure freely (merge, split, rename), which keeps the space compact: few dimensions,
    well aligned with decisions (best dimension-to-decision Jaccard here).
- **Cons:**
  - **Collapse:** past a few hundred values the model compresses its output and silently drops values, even
    when told not to (C2: 241 → 80 values at update 8). Dropped values cannot come back later.
  - Unstable and untraceable: whole branches appear and disappear between iterations; there is no record of
    what was removed or why.

### `rewrite_restore` (rewrite + restore; an ablation control)

- **How it works:** exactly `rewrite`, followed by a deterministic step: every value of the previous taxonomy
  that has supporting documents and that the rewrite dropped (no updated value has the same normalized label)
  is put back, into the dimension of the same name, or into its previous dimension recreated. Restorations
  are logged in the run's `operation_log`.
- **Purpose:** separates the effect of *never losing evidence-backed values* from the effect of *editing
  through operations* (`tools`).
- **Pros:**
  - Nothing supported by evidence is ever lost: highest recall of options and decisions.
  - Keeps the rewrite's freedom to restructure.
- **Cons:**
  - **Accumulation:** the space only grows. The rewrite keeps dropping values and the restore keeps putting
    them back (2,116 restorations in the C2 run), so near-duplicates and renamed variants pile up (525 values
    at the end of the loop, 381 kept by selection for 57 expert options).
  - **Cost:** the whole, ever larger taxonomy is re-sent and re-emitted in every update (13.7M tokens, 3×
    rewrite).
  - Recall is partly bought by volume: option Jaccard no better than rewrite; lowest in-run quality score.

### `tools` (tool-based editing)

- **How it works:** the model never re-emits the taxonomy. It sees a compact view (ids, labels, statuses,
  relations) and the new open codes, and changes the taxonomy only by calling coding operations (LangChain
  tools): `add_value`, `add_evidence`, `move_value`, `merge_values`, `relabel_value`, `set_status`,
  `remove_value`, `add_dimension`, `rename_dimension`, `split_dimension`, `merge_dimensions`,
  `remove_dimension`, `add_relation`, `remove_relation`, `finish`. A `TaxonomyEditor` validates every call
  before applying it (evidence only from the batch; supported values cannot be removed; splits keep ≥ 2
  candidates per part; merges need identical status; a rejected call changes nothing) and replies with
  `ok: …` or an error the model can correct. The loop ends when `finish` is accepted (only after a turn
  without failed calls), or after `edit_max_steps` turns. Every update's operations, rejected calls, uncited
  documents, stop reason and transcript are saved in the `operation_log`.
- **Pros:**
  - No collapse: the space grows steadily and changes only through logged operations (an audit trail of
    the axial coding).
  - Most compact value set relative to its coverage: best one-to-one option Jaccard and in-run quality score.
  - Cheaper than `rewrite_restore` (8.6M tokens).
- **Cons:**
  - The model restructures less than in a rewrite: dimensions fragment (20 dimensions for 7 decisions),
    which lowers dimension-to-decision scores.
  - Selection now loses options (42 present after consolidation → 32 selected).
  - Behavior depends on the prompt and tool replies; two fixes were needed before this comparison: a rule
    that values are design options rather than copies of codes, and similar-value hints in `add_value`
    replies (smoke run: 77% → 23% of values copied an open-code label).
  - About twice the tokens of rewrite.

---

## 3. Results (C2, one run per strategy)

Same configuration and code for all three runs (`examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml`
with only `edit_mode` changed); generation, evaluation and matching LLM `gpt-5.6-luna`; ground truth at
commit `0217b6b`. Cells show **paper view / model view**.

Rows marked *round 2* come from a later run with the changes of section 3b (tools mode with the
decision-point granularity rule and structural check; the selection variants with and without the LLM
relevance filter). Round 1 rows are the first comparison.

### Table 1: dimensions vs. decisions (strict alignment; C2 has 7 decisions)

| Strategy | Dimensions selected | Precision | Recall | F1 | Jaccard |
|---|---|---|---|---|---|
| rewrite | 8 | **0.50 / 0.63** | 0.57 / 0.71 | **0.53 / 0.67** | **0.36 / 0.50** |
| rewrite_restore | 20 | 0.35 / 0.35 | **1.00 / 1.00** | 0.52 / 0.52 | 0.35 / 0.35 |
| tools (round 1) | 20 | 0.20 / 0.20 | 0.57 / 0.57 | 0.30 / 0.30 | 0.17 / 0.17 |
| tools + M2, filter on (round 2) | 15 | 0.33 / 0.40 | 0.71 / 0.86 | 0.45 / 0.55 | 0.29 / 0.38 |
| tools + M2, filter off (round 2) | 19 | 0.32 / 0.37 | 0.86 / **1.00** | 0.46 / 0.54 | 0.30 / 0.37 |

Lenient alignment F1: rewrite 0.65 / 0.79; rewrite_restore 0.75 / 0.82; tools 0.47 / 0.51; tools + M2
filter on 0.60 / 0.71; filter off 0.64 / 0.69.

### Table 2: values vs. options (C2 has 57 / 62 options)

| Strategy | Values compared (paper view) | Precision | Recall | F1 | Jaccard |
|---|---|---|---|---|---|
| rewrite | 40 | 0.28 / 0.33 | 0.23 / 0.26 | 0.25 / 0.29 | 0.13 / 0.15 |
| rewrite_restore | 315 | 0.37 / 0.39 | **0.93 / 0.92** | 0.53 / 0.55 | 0.14 / 0.15 |
| tools (round 1) | 116 | 0.34 / 0.37 | 0.58 / 0.60 | 0.43 / 0.46 | 0.21 / 0.21 |
| tools + M2, filter on (round 2) | 148 | **0.41 / 0.42** | 0.79 / 0.79 | 0.54 / 0.55 | **0.25 / 0.25** |
| tools + M2, filter off (round 2) | 187 | **0.41 / 0.42** | 0.91 / 0.90 | **0.56 / 0.57** | **0.25 / 0.25** |

Exact (`same`-only) option recall, paper view: rewrite 0.04, rewrite_restore 0.44, tools 0.19, tools + M2
0.21 (filter on) / 0.26 (filter off).

### Run statistics

| Strategy | Values per iteration (generate → updates → review → consolidated) | Selected dimensions / values | Tokens | Time | In-run quality score |
|---|---|---|---|---|---|
| rewrite | 54, 118, 171, 95, 184, 89, 145, 241, **80**, 81, 81 | 8 / 70 | 4.5M | 31 min | 0.60 |
| rewrite_restore | 49, 72, 153, 212, 353, 353, 401, 485, 525, 525, 484 | 20 / 381 | 13.7M | 33 min | 0.49 |
| tools (round 1) | 65, 83, 97, 143, 199, 237, 262, 266, 269, 269, 268 | 20 / 182 | 8.6M | 36 min | 0.61 |
| tools + M2 (round 2) | 67, 122, 147, 169, 219, 226, 255, 258, 262, 265, 262 | 15 / 208 (filter off: 19 / all) | 10.5M | 36 min | 0.70 |

### Stage funnel (paper view: expert options present at each stage)

| Strategy | Open codes | Peak in loop | Review | Consolidated | Selected | Largest loss |
|---|---|---|---|---|---|---|
| rewrite | 56 | 39 (update 4) | 16 | 14 | 13 | update 8: 22 options lost for good |
| rewrite_restore | 57 | 53 (review) | 53 | 49 | 50 | consolidation: 5 |
| tools (round 1) | 56 | 44 (update 7) | 44 | 42 | 32 | selection: 10 |
| tools + M2 (round 2) | 57 | 46 (update 7) | 45 | 44 | 41 (filter off: 44) | selection: 7 |

Almost every expert option is open-coded in every run; the strategies differ in what survives the loop and
the steps after it.

### 3b. Round 2: what changed and what it shows

Changes after round 1 (logged in `benchmark/README.md`, "Changes after scores were seen"; general rules, no
threshold tuned to the scores):

- **Tools mode, decision-point granularity (M2):** the tools prompt asks to merge sibling dimensions that
  answer parts of one design question; `finish` asks once for a structural check when an update created
  dimensions.
- **`taxonomy.relevance_selection`:** a switch for the LLM use-case relevance filter at selection. The run
  used the default (`true`); the filter-off view was rebuilt from the same run without an LLM
  (`benchmark/selection_variant.py`), so both selection variants come from one run.

What round 2 shows (one run):

- **Less fragmentation:** 19 consolidated dimensions instead of 30, mostly because the model created fewer
  dimensions (10 splits in the run, no `merge_dimensions` call; the structural check fired 3 times).
  Strict decision F1 0.30 → 0.45 (filter on), decision Jaccard 0.17 → 0.29.
- **Better value-level fit:** option precision 0.34 → 0.41, Jaccard 0.21 → 0.25, F1 0.43 → 0.54.
- **Every update ended with `finish`** (round 1 smoke runs hit the step limit); in-run quality score 0.61 →
  0.70; tokens 8.6M → 10.5M.
- **The relevance filter still costs options:** it dropped 4 reward-design and mitigation dimensions and 7
  options, with no precision gain (0.41 either way). Without it, option recall is 0.91 and every decision is
  covered at the lenient level.
- **Against `rewrite_restore`:** tools + M2 (filter off) reaches similar recall (0.91 vs. 0.93) and higher
  F1 (0.56 vs. 0.53) with half the values compared (187 vs. 315), a much better Jaccard (0.25 vs. 0.14) and
  fewer tokens (10.5M vs. 13.7M); `rewrite_restore` keeps the better decision-level scores.
- **Caution:** round 2 differs from round 1 in the prompt and in run-to-run variation; with one run each, the
  two cannot be separated.

### 3c. C1 check: tools + M2, relevance filter on and off

One tools-mode run on C1 (ML workflow; 10 decisions and 43 options in the paper view, 28 decisions and 121
options in the model view), same code and settings as C2 round 2: 44 min, 17.5M tokens; outputs in
`examples/c1-ml-workflow/u7/`.

- **Relevance filter on vs. off:** identical on C1. The filter kept all 30 dimensions, so both variants are
  the same taxonomy. The filter neither helps nor hurts here; on C2 it cost options.
- **Reference:** the only earlier C1 run is the 2026-10-02 rewrite run, made with older update and review
  prompts (before commit `afebe10`) and scored with the same judge. It is not a like-for-like comparison.

| C1 (paper / model view) | Option P | Option R | Option F1 | Option J | Decision P | Decision R | Decision F1 | Decision J |
|---|---|---|---|---|---|---|---|---|
| rewrite, 2026-10-02 (older prompts) | **0.52 / 0.65** | 0.65 / 0.55 | **0.58** / 0.60 | **0.26** / 0.29 | **0.57 / 0.84** | 0.80 / 0.57 | **0.67** / 0.68 | **0.50** / 0.52 |
| tools + M2 (filter on = off) | 0.38 / 0.58 | **0.79 / 0.75** | 0.51 / **0.66** | 0.19 / **0.30** | 0.45 / 0.77 | **1.00 / 0.82** | 0.62 / **0.79** | 0.45 / **0.66** |

Decision values are for the strict alignment; lenient decision F1 for tools + M2 is 0.87 / 0.88.

- **Run statistics:** values per iteration 76 → 344 with no collapse (rewrite 2026-10-02: oscillating); 30
  dimensions and 344 values selected; every update ended with `finish`; in-run quality score 0.57.
- **Funnel (paper view):** 42 of 43 options open-coded; 29 present after the first draft and about 32 through
  the whole loop, review, consolidation and selection. The options lost are lost at the first draft (6) and
  never added later; nothing is lost at selection.
- **Reading:** on C1, tools mode has higher recall in both views and better scores in the model view (the
  authors' full model, 28 decisions), but lower precision and F1 in the paper view: many of its values match
  parts of the model the paper omits, which the paper view leaves out. The size of the space (344 values,
  30 dimensions) fits the full model better than the paper's 10 decisions.

---

## 4. Reading

- **Never losing evidence-backed values explains most of the recall gain** over `rewrite`: `rewrite_restore`
  recovers 93% of the options, `tools` 58%. Tool-based editing as such is not what lifts recall.
- **F1 alone favors the largest space.** Lenient hits (*broader*/*narrower*) let many redundant values each
  count as a hit, so precision stays flat (0.28–0.37) while recall grows with volume. Jaccard (one-to-one)
  shows the redundancy: `rewrite_restore` is no better than `rewrite` there, `tools` is best.
- **Decision structure:** `rewrite` keeps the fewest, best-aligned dimensions; `tools` and `rewrite_restore`
  fragment the 7 decisions over 20 dimensions.
- **Report together:** option and decision precision, recall, F1 and Jaccard, plus the size of the space,
  so a strategy cannot win by size alone.

## 5. Caveats

- One run per strategy. The rewrite collapse is stochastic (the 2026-10-02 rewrite run had option recall 0.40
  vs. 0.23 here).
- The matching LLM is the generator (`gpt-5.6-luna`); its labels are not independent and are not yet
  validated against human labels (A6).
- C2 only; C1 not yet run.

## 6. Open questions and next steps

0. Decide whether the study configs use `relevance_selection: false` (C2 round 2: the filter costs 7 options
   and gains no precision; C1: the filter keeps every dimension, no effect) or keep the filter; the use-case
   wording is part of human check 3.
1. Repeat the runs (≥ 3 seeds per strategy) before any claim.
2. Decide the paper's metric set (proposed: option and decision P/R/F1 + Jaccard + space size).
3. `rewrite_restore`: limit accumulation (e.g. restore only values with no near-duplicate in the rewrite;
   stronger consolidation), and its token cost.
4. `tools`: reduce dimension fragmentation and the selection loss (selection tuning, dimension merging,
   structural prompts or critic feedback).
5. Run C1.

## 7. Files

- Runs, scores and funnels: `examples/c2-rl-monitoring/u7/` (`c2-u7-<strategy>_taxonomy_*.json`, round 2
  `c2-u7b-tools_*`, `*_gt_metrics.json`, `*_gt_alignment.csv`, `*_stage_funnel.*`). The full match files of
  rewrite_restore and the tools runs, and the derived filter-off taxonomy, are not committed (reproducible
  from the judge cache and `benchmark/selection_variant.py`).
- Implementation plan: `docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md`.
- Progress log: `docs/paper/SANER2027_PAPER_PLAN.md`, §8.7 (2026-10-05 entry).
- Settings: `SETTINGS.md` (`taxonomy.edit_mode`, `taxonomy.edit_max_steps`).
