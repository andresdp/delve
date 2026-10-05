# C2 update-strategy comparison (preliminary, 2026-10-05)

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

### Table 1: dimensions vs. decisions (strict alignment; C2 has 7 decisions)

| Strategy | Dimensions | Precision | Recall | F1 | Jaccard |
|---|---|---|---|---|---|
| rewrite | 8 | 0.50 / 0.63 | 0.57 / 0.71 | 0.53 / 0.67 | **0.36 / 0.50** |
| rewrite_restore | 20 | 0.35 / 0.35 | **1.00 / 1.00** | 0.52 / 0.52 | 0.35 / 0.35 |
| tools | 20 | 0.20 / 0.20 | 0.57 / 0.57 | 0.30 / 0.30 | 0.17 / 0.17 |

Lenient alignment F1: rewrite 0.65 / 0.79; rewrite_restore 0.75 / 0.82; tools 0.47 / 0.51.

### Table 2: values vs. options (C2 has 57 / 62 options)

| Strategy | Values compared (paper view) | Precision | Recall | F1 | Jaccard |
|---|---|---|---|---|---|
| rewrite | 40 | 0.28 / 0.33 | 0.23 / 0.26 | 0.25 / 0.29 | 0.13 / 0.15 |
| rewrite_restore | 315 | **0.37 / 0.39** | **0.93 / 0.92** | **0.53 / 0.55** | 0.14 / 0.15 |
| tools | 116 | 0.34 / 0.37 | 0.58 / 0.60 | 0.43 / 0.46 | **0.21 / 0.21** |

Exact (`same`-only) option recall, paper view: rewrite 0.04, rewrite_restore 0.44, tools 0.19.

### Run statistics

| Strategy | Values per iteration (generate → updates → review → consolidated) | Selected dimensions / values | Tokens | Time | In-run quality score |
|---|---|---|---|---|---|
| rewrite | 54, 118, 171, 95, 184, 89, 145, 241, **80**, 81, 81 | 8 / 70 | 4.5M | 31 min | 0.60 |
| rewrite_restore | 49, 72, 153, 212, 353, 353, 401, 485, 525, 525, 484 | 20 / 381 | 13.7M | 33 min | 0.49 |
| tools | 65, 83, 97, 143, 199, 237, 262, 266, 269, 269, 268 | 20 / 182 | 8.6M | 36 min | 0.61 |

### Stage funnel (paper view: expert options present at each stage)

| Strategy | Open codes | Peak in loop | Review | Consolidated | Selected | Largest loss |
|---|---|---|---|---|---|---|
| rewrite | 56 | 39 (update 4) | 16 | 14 | 13 | update 8: 22 options lost for good |
| rewrite_restore | 57 | 53 (review) | 53 | 49 | 50 | consolidation: 5 |
| tools | 56 | 44 (update 7) | 44 | 42 | 32 | selection: 10 |

Almost every expert option is open-coded in every run; the strategies differ in what survives the loop and
the steps after it.

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

1. Repeat the runs (≥ 3 seeds per strategy) before any claim.
2. Decide the paper's metric set (proposed: option and decision P/R/F1 + Jaccard + space size).
3. `rewrite_restore`: limit accumulation (e.g. restore only values with no near-duplicate in the rewrite;
   stronger consolidation), and its token cost.
4. `tools`: reduce dimension fragmentation and the selection loss (selection tuning, dimension merging,
   structural prompts or critic feedback).
5. Run C1.

## 7. Files

- Runs, scores and funnels: `examples/c2-rl-monitoring/u7/` (`c2-u7-<strategy>_taxonomy_*.json`,
  `*_gt_metrics.json`, `*_gt_alignment.csv`, `*_stage_funnel.*`). The full match files of rewrite_restore
  and tools are not committed (reproducible from the judge cache).
- Implementation plan: `docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md`.
- Progress log: `docs/paper/SANER2027_PAPER_PLAN.md`, §8.7 (2026-10-05 entry).
- Settings: `SETTINGS.md` (`taxonomy.edit_mode`, `taxonomy.edit_max_steps`).
