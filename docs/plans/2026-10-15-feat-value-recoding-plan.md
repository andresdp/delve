---
title: "feat: value recoding — redefine a dimension's values as exclusive alternatives (exclusivity cause i)"
type: feat
status: proposed (2026-10-15), not implemented; verification order C3, then C1 and C2
date: 2026-10-15
related: >-
  docs/plans/2026-10-15-feat-value-exclusivity-plan.md (measure, results, E1–E5),
  src/taxonomy_generator/evaluation/exclusivity.py, src/taxonomy_generator/nodes/{value_consolidator,exclusivity_repair}.py,
  src/taxonomy_generator/evaluation/gt_match.py, src/taxonomy_generator/wiki/model.py
---

# Value recoding

## Goal

A dimension is a system perspective that admits several, mostly exclusive choices; a system should take one value
per dimension. When a system takes several values of one dimension, either (i) the values were not defined as
exclusive alternatives, or (ii) the dimension groups non-exclusive concerns. This plan tackles **(i)** without
changing the notion of dimension and without adding dimensions (user, 2026-10-15). It targets C1 and C2 (the
larger cases) and must not degrade C3.

## Evidence (offline, existing runs, no LLM)

Low-exclusivity dimensions (exclusivity < 0.8, ≥ 2 adopting sources); a source's **combination** is the set of a
dimension's values it adopts.

| | C1 | C2 | C3 (loop feedback run) |
|---|---|---|---|
| Low-exclusivity dimensions | 19 of 19 | 6 of 10 | 20 of 25 |
| Adopting sources per dimension | 11.8 | 8.0 | 2.6 |
| Sources whose combination recurs (≥ 2 sources share it) | 45% | 59% | 0% |
| Combination pairs that nest ({x} ⊂ {x, y}) | 48% | 69% | 72% |
| Dimensions with ≥ 60% of sources on recurring combinations | 4 | 2 | 0 |
| … with 30–60% | 9 | 4 | 0 |

Alternatives tried or ruled out: loop feedback and the repair (no reliable gain, plan E5); coalescing values always
adopted together (3–6 such pairs in C1/C2); splitting into never-co-adopted groups (0 of 25 C1/C2 dimensions
feasible). Recurring combinations are the one signal C1/C2 have: several sources take the same mix of values, which
suggests one alternative described through several values.

## Strategy: the adjustment

For each eligible dimension, the LLM rewrites the values as **alternative answers to the dimension's question** and
assigns every observed combination to exactly one of them. Old values are kept inside the new ones as **facets**
(`includes`), so no evidence or detail is lost.

Example (C1, ML provenance): sources adopt {metadata store, metric recording}, {metric recording}, {metadata store,
lineage} … → *ad-hoc metric logging* / *experiment tracking* / *metadata store with lineage*, each including the
old values it covers.

### Steps

1. **Select (deterministic).** Dimensions with exclusivity < `recoding_min_exclusivity` (0.8), ≥
   `recoding_min_sources` adopting sources (3), and ≥ `recoding_min_recurring` (0.3) of sources on recurring
   combinations. Dimensions failing the last test are not recoded; they are listed as **likely cause (ii)**
   (the dimension groups several concerns) in the log, the report and the wiki.
2. **Propose (one structured LLM call per dimension).** Input: use case, dimension (name, question), current
   candidate values, the combinations with their sources and counts, ≤ 3 short passage excerpts per combination.
   Output: new values (`label`, `description`, `includes`: old value ids), one assignment per combination,
   `keep` when the values already are alternatives, and a rationale.
3. **Validate (deterministic, reject the dimension's proposal on failure).**
   - every new value is adopted by ≥ 2 sources through its assigned combinations (no per-source bundles);
   - ≥ 2 new values, and no more than the old candidate values;
   - every old candidate value is included in ≥ 1 new value; every combination is assigned to exactly one;
   - values whose evidence is only rejections stay as they are (recoding uses adoptions).
   One retry with the validation errors, as in the repair.
4. **Apply.** New values get `includes` (old id, label, description), `supporting_doc_ids` = passages of the
   assigned sources that support an included value, `stances.accepted` likewise; ids renumbered within the
   dimension; old values recorded on the value as `recoded_from`. Evidence summaries recomputed.
5. **Log.** `operation_log` entry `value_recoding`: dimensions selected, recoded, kept, rejected, likely cause
   (ii); the before/after measures below.

Place: after evidence linking in `consolidate_values`, before selection (same place as the repair; the repair stays
off). Setting `taxonomy.value_recoding` (default **false** until verified).

### Measures (exclusivity alone is not the result)

After recoding, exclusivity is high partly by construction, so the claims rest on:

- **Fit:** share of sources whose combination is fully covered by the one new value it was assigned to.
- **Generality:** share of candidate values adopted by ≥ 2 sources (must not fall).
- **Size:** values and dimensions (no new dimensions; fewer values expected).
- **Expert-option coverage** (C1, C2: ground truth): candidate-decision recall and precision from `--match-gt`,
  facet-aware (below). The decisive measure for the paper.
- Exclusivity before/after, and the judge's scoreboard (one sample; noisy).

## Change impact

| Area | Change | Risk |
|---|---|---|
| `evaluation/exclusivity.py` | combinations per dimension, recurring share, fit, generality | low; pure functions |
| `nodes/value_recoding.py` (new) | select, propose, validate, apply, log | medium; new step, off by default |
| `prompts/value_recoding.md`, `schemas.py` | prompt and `RecodingOutput` | low |
| `nodes/value_consolidator.py` | call the step when enabled | low |
| `settings.py`, `configuration.py`, `config.yaml`, `ddspace.yaml` template, `USAGE.md` | `value_recoding`, `recoding_min_exclusivity`, `recoding_min_sources`, `recoding_min_recurring` | low |
| `evaluation/gt_match.py` | **facet-aware matching**: a value's `includes` are offered as match candidates mapped to the value. Opt-in (`matcher.use_facets`), so earlier metrics stay reproducible | **medium**: touches the paper's main metric; must be reported as a setting |
| `wiki/model.py`, `query` | value pages list "Includes"; dimension pages note recoding or likely cause (ii); `raw/graph.json` value nodes carry `includes` | low |
| `report_renderer.py`, `pipeline_cli.py` | one log line and a short report section | low |
| Design points, labeling, `ddspace` commands | unchanged (new values are ordinary values) | none |
| Tests | measure functions, validation rules, apply/evidence, retry, facet-aware match | — |

Effort: about half a day of code and tests.

## Verification (order requested: C3 first)

C3 has no expert ground truth and, per the table above, **no recurring combinations**: with the guards, step 1
should select few or no dimensions. C3 therefore verifies **safety and mechanics**, not effectiveness:

1. **C3 replay, guards on** (saved loop-feedback run; consolidation onward): expected few or no recodings;
   check that nothing degrades (values, dimensions, generality, scoreboard) and the cause-(ii) list is sensible.
   Cost: a few calls plus the judge scoreboard.
2. **C3 replay, guards relaxed** (`recoding_min_recurring: 0`, `≥ 1` source per new value): a **negative
   control**. It should produce per-system bundles (fit high, generality low); this shows what the guards prevent.
   Cost: ~20 calls plus the scoreboard.
3. Review both with the user (values before/after per dimension, generated as a table).
4. **C1 and C2 replays** (saved runs), then `--match-gt` facet-aware and not, against the 10-02 baselines.
   Cost: ~20 calls per case plus the matches.
5. A full run per case only if the replays show a gain in expert-option coverage.

## Open questions

- Should a recoded dimension keep old values that no source adopts (only rejected)? Proposed: yes, unchanged.
- Facet-aware matching changes the metric definition; the paper would report both numbers.

## Results (2026-10-15, replays on saved runs)

Guards as implemented: distinct facet sets per alternative (nested levels allowed), fit ≥ 0.5, ≥ 2 sources per new
value, one retry. (A first guard, "a facet of its own per alternative", rejected exactly the nested levels recoding
is for; replaced.)

**C3** (loop-feedback run): guards on → no dimension eligible (no shared combinations), 9 flagged as likely cause
(ii), nothing changed. Guards relaxed (control) → 4 of 20 recoded into broad per-system "styles" (fit 0.36,
generality 0.32 → 0.30): what the guards prevent.

**C1, C2**: replay of consolidation onward on the 10-02 runs, recoding off vs on; same code, matcher and ground
truth (matching LLM `gpt-5.6-luna` from the study configs; the 10-02 matches used `gpt-5.4-mini` and an older
ground-truth commit, so they are not comparable).

| | Exclusivity | Generality | Values | Recoded | Option P | Option R | Option F1 | Exact R | Decision F1 |
|---|---|---|---|---|---|---|---|---|---|
| C1 off (paper view) | 0.45 | 0.84 | 117 | — | 0.52 | 0.65 | 0.58 | 0.14 | 0.67 |
| C1 on | 0.65 | 0.87 | 107 | 8 of 13 | 0.58 | 0.70 | 0.63 | 0.07 | 0.67 |
| C1 on, facet-aware match | | | | | 0.58 | 0.67 | 0.63 | 0.09 | 0.61 |
| C2 off (paper view) | 0.70 | 0.71 | 56 | — | 0.40 | 0.46 | 0.43 | 0.07 | 0.53 |
| C2 on | 0.87 | 0.76 | 52 | 5 of 8 | 0.44 | 0.58 | 0.50 | 0.05 | 0.53 |
| C2 on, facet-aware match | | | | | 0.44 | 0.53 | 0.48 | 0.05 | 0.53 |

Model view, option F1: C1 0.60 → 0.63, C2 0.45 → 0.54. Recoding raises exclusivity, generality, option precision
and recall in both cases; exact-name recall drops (values are renamed as alternatives); decision F1 unchanged.
Facet-aware matching does not help. One replay per setting; the matching LLM is the generator (not independent).

### Independent matcher and a repeat (2026-10-15)

Matches redone with `--matching-llm openai/gpt-5.4-mini` (independent of the generator; the matcher of the 10-02
baselines, whose numbers the "off" replay reproduces for C1). "on2" is a second recoding replay.

| | Exclusivity | Generality | Values | Recoded | Option F1 paper | Option F1 model | Exact R paper | Decision F1 paper |
|---|---|---|---|---|---|---|---|---|
| C1 off | 0.45 | 0.84 | 117 | — | 0.50 | 0.59 | 0.47 | 0.76 |
| C1 on | 0.65 | 0.87 | 107 | 8 | 0.47 | 0.54 | 0.30 | 0.73 |
| C1 on2 | 0.65 | 0.85 | 112 | 8 | 0.54 | 0.61 | 0.37 | 0.70 |
| C2 off | 0.70 | 0.71 | 56 | — | 0.25 | 0.30 | 0.16 | 0.42 |
| C2 on | 0.87 | 0.76 | 52 | 5 | 0.29 | 0.36 | 0.16 | 0.53 |
| C2 on2 | 0.90 | 0.82 | 48 | 6 | 0.30 | 0.34 | 0.14 | 0.53 |

Exclusivity and generality rise in every replay. Expert-option coverage: C2 improves in both replays (option F1
+0.04 to +0.06, decision F1 +0.11); C1 is neutral (−0.03 and +0.04 option F1, mean about 0) with lower exact-name
recall. With the generator as matcher (`gpt-5.6-luna`) C1 looked +0.05: the non-independent matcher favoured the
recoded values. Conclusion: recoding is a structural improvement (one value per dimension per source) that keeps
expert-option coverage in C1 and raises it in C2.
