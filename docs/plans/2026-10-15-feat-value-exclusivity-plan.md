---
title: "feat: value exclusivity — one value per dimension per system (measured, penalized, repaired); cap applied at selection"
type: feat
status: implemented 2026-10-15 (branch feat/value-exclusivity); measure, loop feedback and cap at selection in use; the repair step is off by default, superseded by value recoding (2026-10-15-feat-value-recoding-plan.md)
date: 2026-10-15
related: >-
  src/taxonomy_generator/nodes/{value_consolidator,evidence_linker,dimension_selector,decision_focus}.py,
  src/taxonomy_generator/evaluation/{runner,design_points}.py, src/taxonomy_generator/wiki/model.py,
  src/taxonomy_generator/taxonomy_editor.py
---

# Value exclusivity

## Problem

A dimension is one design decision; its values are the alternative answers. A system should therefore take one
value per dimension. The C3 wikis show otherwise: systems share many values but few dimensions. Counting only the
values a system's passages **adopt** (accepted stance; system = primary system of the passage):

| Run | Dimensions | Values | System × dimension cells with > 1 adopted value | Median | Max |
|---|---|---|---|---|---|
| Capped at 5 (sample, 10-10) | 5 | 196 | 13 of 19 (68%) | 6 | 29 |
| Uncapped (reference candidate, 10-10) | 31 | 191 | 40 of 59 (68%) | 2 | 9 |

Without a system map (C1, C2: sources as units), the measure works the same: C1 0.45 (124 of 225 source ×
dimension cells with several values), C2 0.71 (25 of 86); C3 by source 0.34.

One passage alone adopts two or more values of one dimension in 41% (uncapped) to 64% (capped) of passage ×
dimension pairs.

Causes:

1. **Values that are not alternatives.** E.g. Spokes, "Replica Commit Coordination": *Three-phase commit*,
   *Majority-based write commitment*, *Git reference transaction locking*: all used together; they answer different
   questions. The prompts already say values are alternative answers, but the LLM judges that from labels; nothing
   checks it against the evidence.
2. **The cap is given to the LLM during generation** (`max_num_clusters` in the generation, update and review prompts;
   the tools editor rejects splits past it), so many decisions get squeezed into a few broad topics (~40 values each).
3. Evidence linking is not the cause: each open code goes to its single best value. A passage gets several values of
   one dimension because it describes several mechanisms.
4. The wiki counts passages that *reject* a value as support of a system (secondary: 79% → 68% when removed).

## Decisions (user, 2026-10-15)

| # | Decision |
|---|---|
| E1 | Exclusivity is the default: a system takes one value per dimension. Not enforced strictly: a combination may be kept as a **declared hybrid**; remaining conflicts are reported, not hidden. |
| E2 | Several adopted values per dimension for one system are **penalized** (a deterministic score that lowers the scoreboard and feeds back into the update loop). |
| E3 | The dimension cap is applied **after mining**, at selection: the top-k decision points are kept; the others are dropped (recorded), not merged in. |
| E4 | Plan and build all now; one C3 run after the user approves the cost. |

## Design

**Unit.** The fix must work without systems as references (C1, C2; user, 2026-10-15). The pipeline has no
system map, so the adopting unit is the **source** (`s03` for passage `s03_p02`);
`ddspace` treats sources as systems. The wiki uses the passage → system map when one is given (C3), else sources.

**Adoption.** A unit adopts a candidate value when one of its passages is in the value's `stances.accepted` (or, for
values without stances, in `supporting_doc_ids` with status `accepted`). Rejections never count.

**Exclusivity of a dimension** = share of the units adopting at least one of its candidate values that adopt exactly
one. A declared hybrid (a set of values of the dimension) counts as one choice when a unit adopts exactly that set.
Taxonomy exclusivity = mean over dimensions weighted by adopting units. Dimensions no unit adopts are left out.

### U1. `evaluation/exclusivity.py` (deterministic, no LLM)

`adopting_docs`, `dimension_exclusivity`, `taxonomy_exclusivity` (score, per-dimension rows, co-adopted value pairs
with their units, ranked). `feedback(report)`: the worst dimensions with the fix each needs (split into the
questions the co-adopted values answer; merge two values that are one option; declare a hybrid).

### U2. Penalty: a deterministic scoreboard row

`run_scoreboard` adds the row **Value exclusivity** (`deterministic: true`) with the score and the U1 feedback as its
reason. It counts in `overall` and, like every row, flows into the next update/review through
`format_evaluation_summary` when it is among the weakest. It needs no judge (it is skipped only when the
whole scoreboard fails).
Setting: `evaluation.exclusivity: true`.

### U3. Repair step (after evidence linking, before selection)

In `consolidate_values`, after `link_evidence` and `drop_unsupported_values`: for each dimension whose exclusivity is
below `taxonomy.exclusivity_min` (default 0.8) with at least `exclusivity_min_units` (default 2) adopting units, one
structured LLM call sees the use case, the dimension, its candidate values and the co-adopted pairs (with up to three
short passage excerpts each) and proposes:

- `split`: the dimension answers several questions; parts with value ids (editor `split_dimension`; each part keeps
  ≥ 2 candidate decisions);
- `extract`: values that answer a sub-question become their own dimension, related to this one by `refines`;
- `merge`: values that are the same option at different granularity (editor `merge_values`);
- `hybrid`: values a system really combines; recorded on the dimension as `hybrids: [{value_ids, reason}]`;
- nothing (keep).

Applied through `TaxonomyEditor(review=True)`, so invalid proposals are rejected and logged; evidence summaries are
recomputed. The before/after exclusivity and the operations go to the explanations, the status log and
`exclusivity_log` on the taxonomy JSON. Setting: `taxonomy.exclusivity_repair: true`. Concurrency 5. A failed call
leaves its dimension unchanged.

### U4. Cap at selection

New `taxonomy.cap_stage: selection | generation` (default `selection`). With `selection`, the generation, update and
review prompts and the tools editor see no cap; `select_dimensions` gives the cap to the selection prompt ("at most k,
most important first") and keeps the first k of its ordered selection; the rest are recorded in
`dropped_dimensions` ("outside the cap of k"). Without the relevance filter, dimensions are ranked by sources, then
exclusivity. `generation` keeps the old behaviour (reproduces the earlier runs).

### U5. Wiki

- System pages and the system × dimension matrix count adopted values only; rejected ones are listed apart
  ("considered and rejected"); a cell with several adopted values is marked, a declared hybrid is shown as such.
- Dimension pages show the exclusivity, the co-adopted pairs and the hybrids.
- Design points: unchanged (the sampler still attests by supporting passages), so the paper's design-point
  numbers stay reproducible; revisit after the paper.
- Source pages list the dimensions where the source adopts several values. Without a system map the dimension
  pages count sources.
- `raw/graph.json` dimension nodes carry `exclusivity`.

### U6. Settings and docs

`settings.py`, `configuration.py`, `config.yaml`, the `ddspace.yaml` template, `USAGE.md` (settings), example configs
untouched (defaults apply). Tests for U1–U5.

## Verification

- Unit tests: exclusivity math (hybrids, rejections, no adopters), scoreboard row and feedback, repair with a fake
  model (split / extract / merge / hybrid / invalid proposals), cap at selection, wiki pages.
- Re-score the existing C3 runs with U1 (no LLM): the table above, reproduced by code.
- One C3 run (uncapped, then the cap selection applied) after approval (~1.5M tokens).

## Out of scope

- A system map in the pipeline (units stay sources).
- Strict enforcement (forcing one value per system).

## Results (2026-10-15)

C3 uncapped run with the repair (1.69M tokens), then the improved repair replayed on its reviewed taxonomy.
Exclusivity by source on the selected view, with the corrected measure (dimensions with fewer than two
candidate decisions or adopted by fewer than two sources left out):

| Run | Dimensions | Exclusivity |
|---|---|---|
| 10-10, no feature | 31 | 0.38 |
| 10-15, first repair | 42 | 0.44 |
| replay, repair with move/outcome and retry | 31 | 0.43 |
| replay, same plus the single-candidate guard | 36 | 0.34 |

Differences are within run-to-run noise (the judge's orthogonality gave 0.30, 0.60 and 0.30 on near-identical
taxonomies). The earlier 0.23 → 0.38 gain was partly an artifact: single-candidate dimensions scored as
exclusive, then selection dropped them.

**Cause.** With five sources that mostly describe one system each, many design questions show one option. The
rule "a decision point needs two candidate decisions" (`min_candidate_decisions: 2`) makes the LLM bundle
unrelated mechanisms into one dimension (e.g. replica locking + majority-vote rollback), and the repair cannot
undo it without creating single-option dimensions.

**Decision (user, 2026-10-15), E5.** Keep the two-candidate rule (no superfluous dimensions) and use exclusivity
as a measure: scoreboard row, loop feedback, wiki. The repair is off by default (`exclusivity_repair: false`).
Low exclusivity weakens the space's discriminative power (several values of a dimension coexist in one design);
it is reported as a limitation of small corpora. Next: one C3 run with the new loop feedback (repair off) to see
whether mining bundles less from the start.

### C3 run with the loop feedback, repair off (2026-10-15, 1.43M tokens)

Selected views, corrected measure; judged scores from the final scoreboard (one judge sample each).

| Run | Dimensions | Candidates per dimension | Exclusivity (systems) | Exclusivity (sources) | One decision point | Axis vs. value | Orthogonality |
|---|---|---|---|---|---|---|---|
| 10-08 | 22 | 6.3 | 0.13 | 0.23 | 0.20 | 0.30 | 0.70 |
| 10-10 | 31 | 4.5 | 0.40 | 0.38 | 0.30 | 0.20 | 0.70 |
| 10-15 repair | 42 | 3.7 | 0.37 | 0.44 | 0.30 | 0.30 | 0.30 |
| 10-15 loop feedback | 25 | 5.6 | 0.47 | 0.33 | 0.40 | 0.50 | 0.30 |

In the loop, exclusivity stayed flat (0.35, 0.31, 0.33 at iterations 4, 6, 8). The loop feedback gives a more
compact taxonomy with the best "one decision point" and "axis vs. value" scores, but no clear change in
exclusivity: it is within run-to-run noise (one run per setting). Exclusivity stays a measure and a reported
limitation; the loop feedback is kept (no cost beyond embeddings).

**Reproduce.** Runs: `examples/c3-git-at-scale/exclusivity-20261015/` (repair on) and `loopfeedback-20261015/`
(loop feedback, repair off); repair variants replayed with `benchmark/replay_consolidation.py … --set
exclusivity_repair=true`. Exclusivity of any saved run: `taxonomy_exclusivity` in `evaluation/exclusivity.py`.

### Prompting values as alternatives, and a co-adoption warning (2026-10-16, branch `feat/value-alternatives-prompts`, parked)

**Changes** (commit `8fd22c5`):

1. The tools prompt's granularity rule, and `finish`'s structural check, no longer advise "fewer, broader decision
   points": they merge sibling dimensions only when their values are rival answers to one question.
2. An operational test for alternatives in the generation, update, review and tools prompts: "a system takes one
   value *instead of* another; values one system uses together are complementary".
3. A deterministic editor warning in `add_value` and `add_evidence`: the source of the cited documents already
   adopts another accepted or mixed value of the same dimension.

**Test.** C3 sample config (cap 8 at selection; mining uncapped); 2 baseline runs (`feat/ddspace-tool`, `bf3490d`)
and 2 treatment runs. Outputs are in `output/ab-exclusivity/`, gitignored. The uncapped view is rebuilt with the
support rules (no LLM).

| | Excl. by source (cap 8) | Excl. by system (cap 8) | Excl. by source (uncapped) | Generality (cap 8) | Max values per dimension | Overall |
|---|---|---|---|---|---|---|
| Baseline 1 / 2 | 0.35 / 0.56 | 0.33 / 0.43 | 0.26 / 0.42 | 0.39 / 0.50 | 33 / 16 | 0.65 / 0.70 |
| Treatment 1 / 2 | 0.29 / 0.40 | 0.15 / 0.25 | 0.29 / 0.32 | 0.43 / 0.42 | 12 / 12 | 0.63 / 0.66 |

**Result: no gain.**
- The baselines alone differ by 0.21. By system, both treatment runs score below both baselines.
- Dimensions are narrower (at most 12 values), but the judged orthogonality, "one decision point" and "axis vs. value"
  do not improve.
- **The warning fires 163–176 times per run**, on most of the roughly 250 additions. Each C3 source describes one
  system combining many techniques, so the signal is everywhere and the model mostly ignores it: it moved 5 and 21
  values, against 4 and 8 in the baselines. Where it acts, the fix (a technique in its own decision) usually needs
  a dimension with a single candidate, which `min_candidate_decisions: 2` forbids: the same small-corpus limit as
  the repair step (E5).

**Decision (user, 2026-10-16):** not used in the main runs; the method stays as on `feat/ddspace-tool`. The branch
is parked. The changes may behave differently on C1/C2 (about 30 sources, each covering several systems), where
the warning would be rarer. That test (about 8M tokens per C1 run) comes after the deadline.
