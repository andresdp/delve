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
