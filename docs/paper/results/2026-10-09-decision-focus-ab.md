# Decision-focus pass: offline A/B (2026-10-09)

Experiments of the plan `docs/plans/2026-10-08-1500-feat-decision-focus-pass-plan.md`, run one at a time on saved runs. Each experiment builds a variant of the same base run (`benchmark/focus_variant.py`), scores it against the ground truth with the same matcher settings, judge and cache (`python main.py --match-gt`), compares it with the base (`benchmark/focus_compare.py`), and runs the quality probe (luna judge). The keep/drop rule (KTD3) was fixed before E1 was scored.

**Base runs** (judge and generator: `openai/gpt-5.6-luna`):

| Case | Base run | Dimensions (selected) |
|---|---|---|
| C1 | `examples/c1-ml-workflow/u7/c1-u7b-tools_taxonomy_20261005_122709.json` | 30 |
| C2 | `examples/c2-rl-monitoring/u7/c2-u7b-tools-norelevance_taxonomy_20261005_110747.json` | 19 |
| C3 | `examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350.json` | 22 |

**Like-for-like check (before E1).** A no-change variant of C2 (stub model, no proposals) reproduced the baseline exactly: every metric in both views, 0 re-judged pairs, 0 label changes.

---

## E1. Merge sibling dimensions

**Variant:** `-merge`. One LLM call per case proposes groups of dimensions that are parts of one design decision (prompt `src/taxonomy_generator/prompts/decision_focus_merge.md`).

**What happened:** the model proposed **no groups** on any case (C1, C2 and C3: 0 applied, 0 rejected, 0 failed calls). The variants are the base taxonomies unchanged; evidence summaries were recomputed, and C3's selection keeps the same 22 dimensions.

**Ground-truth scores:** identical to the baselines in both views for C1 and C2 (all deltas 0).

**Judge-noise counts (KTD6):**

| Case | Pairs | Re-judged | Label changes on unchanged pairs | By transition |
|---|---|---|---|---|
| C1 | 31,339 | 3 | 5 | auto→judge 1, judge→auto_rank 2, auto_rank→judge 2 |
| C2 | 12,096 | 0 | 0 | — |

None of C1's changes is judge-to-judge. They come from re-computed embeddings: tiny numerical differences move a few borderline pairs across the matcher's distance threshold or its nearest-neighbour cut-off. They did not change any metric.

**Quality probe on identical taxonomies (probe noise):**

| Case | Focused rate (base → rerun) | Candidate values for another question (base → rerun) |
|---|---|---|
| C1 | 0.233 → 0.200 | 0.309 → 0.340 |
| C2 | 0.526 → 0.474 | 0.203 → 0.224 |
| C3 | 0.318 → 0.318 | 0.223 → 0.252 |

The probe moves by up to 5 points on an unchanged taxonomy, so its rates cannot decide a verdict (as KTD3 already states).

**Verdict: dropped (no effect).** The merge pass made no change, so it cannot meet KTD3's minimum gain.

**Reading:**
- The over-splitting seen against the expert models is not a set of obvious siblings that an LLM, asked with the same caution as the pipeline's merge judge ("when uncertain, keep them separate"), recognizes as one decision.
- The pipeline already merges near-duplicate dimensions during consolidation (embedding distance plus an LLM judge), with a similar rule. The new pass adds nothing at that caution level.
- A less cautious merge prompt would be a new experiment designed after seeing this result, so it would have to be reported as such.

---

## E2. Rehome values

**Variant:** `-rehome`. One LLM call per dimension proposes, for each value, `keep`, `move` (to the dimension whose question it answers) or `outcome` (a goal, principle or effect) (prompt `src/taxonomy_generator/prompts/decision_focus_rehome.md`).

**What happened:** no proposal was rejected and no call failed.

| Case | Values moved | Candidate values turned into outcomes | Proposals for values already outcomes (no-ops) |
|---|---|---|---|
| C1 | 35 | 15 (11 accepted, 4 mixed) | 82 |
| C2 | 23 | 4 (2 accepted, 1 mixed, 1 rejected) | 68 |
| C3 | 26 | 9 (accepted) | 46 |

The no-ops did not change the taxonomy. They were logged as applied operations; the pass now skips them and counts them as `unchanged`. No dimension was emptied, so the selections keep 30, 19 and 22 dimensions.

**Ground-truth scores** (base → variant; Δ):

| Metric | C1 paper | C1 model | C2 paper | C2 model |
|---|---|---|---|---|
| Decision P (strict) | 0.45 → 0.53 (+0.07) | 0.77 → 0.73 (−0.03) | 0.32 → 0.32 (0) | 0.37 → 0.37 (0) |
| Decision R (strict) | 1.00 → 1.00 (0) | 0.82 → 0.79 (−0.04) | 0.86 → 0.86 (0) | 1.00 → 1.00 (0) |
| Decision F1 (strict) | 0.63 → 0.69 (+0.06) | 0.79 → 0.76 (−0.03) | 0.46 → 0.46 (0) | 0.54 → 0.54 (0) |
| Decision F1 (lenient) | 0.87 → 0.88 (+0.01) | 0.88 → 0.90 (+0.02) | 0.64 → 0.73 (+0.09) | 0.69 → 0.77 (+0.08) |
| Option P | 0.38 → 0.40 (+0.02) | 0.58 → 0.61 (+0.02) | 0.41 → 0.42 (+0.01) | 0.42 → 0.43 (+0.01) |
| Option R | 0.79 → 0.77 (−0.02) | 0.75 → 0.74 (−0.02) | 0.91 → 0.89 (−0.02) | 0.90 → 0.89 (−0.02) |
| Option F1 | 0.51 → 0.52 (+0.01) | 0.66 → 0.66 (+0.01) | 0.56 → 0.57 (+0.01) | 0.57 → 0.58 (+0.00) |
| Exact R | 0.16 → 0.16 (0) | 0.21 → 0.21 (+0.01) | 0.26 → 0.26 (0) | 0.27 → 0.27 (0) |
| Placement | 0.82 → 0.83 (+0.01) | 0.86 → 0.87 (+0.01) | 0.67 → 0.70 (+0.03) | 0.68 → 0.75 (+0.08) |

**Judge-noise counts (KTD6):**

| Case | Pairs | Re-judged | Unchanged pairs | Label changes on unchanged pairs | By transition |
|---|---|---|---|---|---|
| C1 | 29,524 | 198 | 25,289 | 25 | judge→auto_rank 8, auto_rank→judge 17 |
| C2 | 11,844 | 133 | 10,458 | 22 | judge→auto_rank 4, auto_rank→judge 18 |

No change on unchanged pairs is judge-to-judge; all come from the matcher's nearest-neighbour routing, which shifts when values move.

**Quality probe** (base → variant): focused rate C1 0.23 → 0.27, C2 0.53 → 0.53, C3 0.32 → 0.32; candidate values for another question C1 0.31 → 0.31, C2 0.20 → 0.23, C3 0.22 → 0.25. All within the probe's rerun noise (E1).

**KTD3 verdict: dropped.**

| Condition (C2 paper / C2 model / C1 model) | Result |
|---|---|
| Option precision or F1 rises by ≥ 0.03 | +0.009 / +0.009 / +0.024: fails |
| Option recall drops by at most 0.03 | −0.018 / −0.016 / −0.017: passes |
| Strict decision F1 does not drop | 0 / 0 / −0.035: fails on C1 |
| Strict decision recall does not drop | 0 / 0 / −0.036: fails on C1 |
| C2 placement rises | +0.026 / +0.075: passes |

**Reading:**
- Rehoming does what it targets on C2: placement rises (+0.03 / +0.08) and lenient decision alignment rises (+0.09 / +0.08), because values move to the decision points the experts would group them under.
- It does not make the taxonomy closer to the experts at the level KTD3 requires. Option precision barely moves, because a move does not change whether a value matches an option. On C1's model view, strict decision alignment loses one expert decision: a decision point that matched it lost the values that made the match.
- The probe does not see fewer off-question values after the moves, which suggests the probe's "other question" judgment and the rehome pass's move judgment disagree on many values, even with the same model.
- The paper view of C1 improves (strict decision F1 +0.06), but it does not decide (Key Decisions).

---

## E3 and E1b: not run

- **E3** (merge, then rehome) would equal E2, because the merge pass made no change. Skipped.
- **E1b** (one less cautious merge prompt, designed after E1's null result) was considered and skipped by the author after the headroom analysis below: on C1 it would almost certainly fail the decision-recall guard of the deciding view.

---

## Analysis: why the dimensions differ from the expert decisions

A diagnostic on the base runs' lenient alignments (`*_gt_alignment.csv`), used only to decide whether further merge experiments are worth running. It uses the ground truth, so it never feeds a prompt or a setting.

An expert decision is **split** when two or more Delve dimensions align with it; a dimension is **cross-cutting** when it aligns with two or more expert decisions; a dimension is **unaligned** when no expert decision shares at least the minimum share of matched options with it.

| | C1 model view | C1 paper view | C2 model view | C2 paper view |
|---|---|---|---|---|
| Expert decisions | 28 | 10 | 7 | 7 |
| Delve dimensions | 30 | 30 | 19 | 19 |
| Aligned dimensions | 25 | 17 | 10 | 9 |
| Unaligned dimensions | 5 | 13 | 9 | 10 |
| Expert decisions split over 2+ dimensions | 19 | 9 | 6 | 5 |
| Cross-cutting dimensions | 22 | 10 | 4 | 4 |

**C1: a different decomposition, not a finer one.** 22 of C1's 30 dimensions each overlap several expert decisions, and one expert decision ("How to automatically process the data used for model building?") spans eight Delve dimensions. The experts decompose the ML workflow by pipeline stage and task. Delve decomposes it by technical concern, e.g. "Data Profiling and Validation" or "Feature Pipeline Architecture and Tooling", and those concerns recur across stages. Merging cannot reconcile two decompositions that cut the same space along different axes. Any substantial merge produces broad dimensions that each strict-align with one decision, so decision recall falls. This is why E2's moves cost one strict alignment on the model view and why E1b was not run.

**C2: mostly scope, partly splits.**
- 9 of C2's 19 dimensions align with no expert decision. They are mainly operational and integration decision points (e.g. telemetry collection, rollout and incident control) that the source passages discuss but the expert model does not include. This gap is about what the use case puts in scope, not about granularity.
- The remaining gap is a small number of true splits: 6 expert decisions are each split over two or three dimensions, e.g. "Production Monitoring Signal Selection" over "Runtime Signal Selection", "Telemetry Collection Architecture" and "Operational Monitoring Integration".
- **Headroom:** merging exactly those splits would take C2's model view from 19 to about 13 dimensions with the same 7 strict matches, raising decision precision from 0.37 to about 0.54 and strict decision F1 from 0.54 to about 0.70. This is a ceiling. It assumes perfect merges, and 4 cross-cutting dimensions make clean merges harder.

**What the precision gap means for the evaluation.**
- Low decision precision against the expert models has three distinct sources, which the paper should not report as one "Delve is too fine-grained" finding:
  1. decision points outside the expert model's scope (C2, unaligned dimensions);
  2. a different but coherent decomposition (C1, cross-cutting dimensions);
  3. true splits of one expert decision (both cases, smaller).
- Only the third is a granularity error in the usual sense. The first two are differences in scope and in decomposition that strict one-to-one alignment counts as false positives.
- Lenient decision alignment already credits the third source, and the gap between lenient and strict F1 is a usable summary of it (C1 model 0.88 vs. 0.79; C2 model 0.69 vs. 0.54).

---

## Outcome

No variant was kept (E1 no effect, E2 dropped under KTD3, E3 and E1b not run). The pipeline is unchanged. The passes, the variant tool and the comparison tool stay in the repository as offline analysis tools:
- `src/taxonomy_generator/nodes/decision_focus.py`;
- `benchmark/focus_variant.py`;
- `benchmark/focus_compare.py`.

Decision-point granularity, decomposition and scope are reported as findings and threats, not fixed. The rehome pass improves placement on C2 and could serve as an optional tool outside the evaluated pipeline.
