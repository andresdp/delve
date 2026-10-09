---
title: "feat: Decision-focus pass after consolidation (deferred)"
type: feat
date: 2026-10-08
origin: docs/paper/results/2026-10-08-taxonomy-quality-probe.md
deferred: true
---

# feat: Decision-focus pass after consolidation (deferred)

**Status: deferred** (user decision 2026-10-08). The wiki/graph export for the paper and an upcoming meeting comes first. Pick this up on its own feature branch before the C1/C2/C3 re-runs and the freeze.

## Problem

The quality probe (`docs/paper/results/2026-10-08-taxonomy-quality-probe.md`) measured the latest tools-mode runs of C1, C2 and the first C3 run.

| Measure | C1 | C2 | C3 |
|---|---|---|---|
| Candidate values (accepted, mixed, rejected) answering a different design question than their dimension, luna judge | 31% | 20% | 22% |
| Same, `gpt-5.4-mini` judge | 26% | 20% | 22% |
| Focused dimensions (no such value), luna | 23% | 53% | 32% |
| Candidate values that are goals, principles or facts rather than options | up to 12% | | |

- **Effects:** bundled decision points lower strict decision alignment against the expert models, make sampled design points (E13) less coherent, and on C3 let a system be compared inside "its own" dimension instead of on a shared axis.
- **The prompts already ask for this:** generation, update and review all say "split broad topics", so more prompt text is unlikely to fix it.
- **Not caused by the 10-05 granularity rule:** C2 before that rule had the same rate (45% focused, 20% other-question values).
- **Per-value labels are unreliable:** the two judges agree on the rate but often flag different values (C1: 34 values flagged by both, 114 by either). A fix must be judged by the ground-truth scores, not by the probe alone.

## Scope

**In:**
- one post-consolidation step that re-homes values and splits bundled dimensions;
- relabeling goals and principles as outcomes;
- an offline A/B on saved runs;
- if kept, integration behind a config switch.

**Out (decided):**
- the evidence-link pipeline: accepted links are sound and the weak spots are small samples;
- the 10-05 granularity rule in `taxonomy_tools.md`: keep it;
- the C3 corpus and the C3 configs: changing them now would tune to the result;
- new prompt text in generation, update or review.

## Approach

### KTD1. Separate step after consolidation, not more prompt text

The step runs on the consolidated taxonomy, before dimension selection. It works one dimension at a time, with luna, the study LLM. It uses the existing `TaxonomyEditor` operations only:
- `move_value` to the dimension whose question the value answers;
- `split_dimension` when each part keeps at least two candidate decisions;
- `set_status` to `outcome` for goals and principles that are not choices;
- `add_dimension` only when a moved value has no home and at least two candidates.

After the step:
- dimension evidence summaries are recomputed from the values' `supporting_doc_ids`;
- selection's rules run unchanged (`min_dimension_sources`, `min_candidate_decisions`).

### KTD2. Offline A/B on saved runs before any pipeline run

Apply the step to the saved consolidated taxonomies of:
- C1 `c1-u7b-tools_taxonomy_20261005_122709`;
- C2 `c2-u7b-tools-norelevance_taxonomy_20261005_110747`;
- C3 `c3-git-at-scale_taxonomy_20261008_115350`.

The tool follows the pattern of `benchmark/selection_variant.py` and writes a `-focus` sibling of each run. Comparing within the same runs removes run-to-run variation.

### KTD3. Keep/drop rule

Keep the step only if, on C1 and C2 (paper and model view, `matching_llm` luna as in the frame):
- option precision or option F1 rises;
- strict decision F1 does not drop;
- option recall drops by at most 0.03.

The probe's focused rate is reported but does not decide: it uses similar criteria and the same LLM, so it would partly confirm itself.

### KTD4. Integration as an ablatable stage

Add a `taxonomy.decision_focus` switch, default `true` if kept. Record it in the run provenance (P13) and in the frame change log (`benchmark/README.md`, "Changes after scores were seen"). The off setting is an ablation for the paper.

## Implementation units

### U1. Focus step module

- **Files:**
  - `src/taxonomy_generator/nodes/decision_focus.py`, using `taxonomy_editor.py`;
  - a prompt in `src/taxonomy_generator/prompts/`;
  - tests in `tests/unit_tests/test_decision_focus.py`.
- **Tests:**
  - a fixture dimension with values for two questions is split, or a value is moved;
  - a split that would leave a part with fewer than two candidates is refused and the value is moved instead;
  - goal values become outcomes;
  - evidence summaries are recomputed;
  - a failed LLM call leaves the dimension unchanged.

### U2. Offline variant tool

- **Files:** `benchmark/focus_variant.py` and its tests.
- **Behaviour:** reads a saved run, applies U1 to its final consolidated clusters, re-applies selection's structural rules, and writes `<name>-focus_taxonomy_<ts>.json`.

### U3. A/B scoring

For each case:
- run `python main.py --match-gt` on the base and focus variants of C1 and C2;
- run `benchmark/quality_probe.py` (luna) on all three.

Write the results to `docs/paper/results/<date>-decision-focus-ab.md` and apply KTD3.

### U4. Pipeline integration (only if kept)

- **Pipeline:** wire U1 into the graph after consolidation and before selection, behind `taxonomy.decision_focus`.
- **Settings:** add the switch to `settings.py`, `configuration.py` and the study configs.
- **Records:** add the frame change-log entry.
- **Tests:** the graph runs with the switch on and off.

## Then

1. Freeze.
2. Re-run C1, C2 and C3 one at a time, never in parallel because of the TPM limit. Approximate tokens per seed: C1 17.5M, C2 10.5M, C3 1.5M.
3. Run three seeds each if time allows.
4. Re-run the design-point sampler (A12) and the probe on the new runs.

## Related: dimension granularity (noted 2026-10-08, to address with this pass)

- **Observation:** Delve mines more, finer-grained dimensions than human analysts write down:

  | Case | Delve dimensions | Expert decisions |
  |---|---|---|
  | C1 | 30 | 10 (paper view) / 28 (model view) |
  | C2 | 19 | 7 |
  | C3 (first run, 48 passages) | 22 | no ground truth |

- **Two causes:**
  - **Corpus effects:** sources with operational or client-side detail yield single-system dimensions. In C3, four Spokes operations dimensions and six Scalar client dimensions.
  - **C3's minimum support of 1:** five single-source dimensions survive.
- **Not the fix: a cap** (`max_num_clusters`). It forces broad topics that bundle decisions (the probe's finding), and changing C3's settings after seeing the output would be post-hoc tuning.
- **To decide here, validated on C1/C2 against the expert decision counts:**
  - is the granularity too fine, or appropriately detailed?
  - should this pass also merge sibling dimensions that answer parts of one decision?
  - should minimum support be stricter for multi-source corpora?
- **Meanwhile (presentation only):** the wiki marks **core dimensions** (evidence from at least 2 sources, or supported by at least 2 systems; `--core-min-sources`, `--core-min-systems`) and has core-only filters. In C3, 18 of 22 are core. Stricter thresholds (3/3, 11 core) drop every client-side dimension, so the threshold itself shapes what looks central.

## Risks

- **Re-fragmentation:** splitting can undo the 10-05 gain in decision F1. KTD3's decision-F1 guard catches this.
- **Self-grading:** luna both edits and judges. The decision rests on the ground-truth scores.
- **Moved values keep their evidence links:** the C3 attested design points are then re-derived, not reused.
