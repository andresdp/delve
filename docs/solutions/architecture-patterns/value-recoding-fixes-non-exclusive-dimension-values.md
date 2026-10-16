---
title: "Non-exclusive dimension values: measure exclusivity, then recode values as alternatives"
date: 2026-10-15
category: architecture-patterns
module: taxonomy_generator
problem_type: architecture_pattern
component: service_layer
severity: medium
applies_when:
  - "A source or system adopts several values of one dimension (low value exclusivity) in an LLM-mined design space"
  - "Several sources share the same, often nested, combination of a dimension's values"
  - "Tempted to fix exclusivity with a loop penalty, an LLM split or merge repair, coalescing, or graph colouring"
  - "Comparing pipeline variants where one full run per setting is within run-to-run noise"
related_components:
  - evaluation
  - taxonomy_editor
tags: [value-exclusivity, value-recoding, decision-points, llm-pipeline, deterministic-validation, replay-evaluation, independent-matcher, fragmentation]
---

# Non-exclusive dimension values: measure exclusivity, then recode values as alternatives

## Context

A dimension is one decision point. Its values should be (mostly) exclusive alternatives: a system takes one value
per dimension. The measure showed otherwise. In C3, 68% of system x dimension cells had more than one adopted value
(capped run: median 6, max 29; uncapped: median 2, max 9). By source, C1 scored 0.45 and C2 0.71
(`docs/plans/2026-10-15-feat-value-exclusivity-plan.md`, lines 22-26).

There are two possible causes. (i) The values were not defined as alternatives. (ii) The dimension groups several
concerns. The user asked to tackle (i), keep the notion of dimension, and add no superfluous dimensions.

Approaches that failed (evidence from the two 2026-10-15 plans and the session brief):

| Approach | Result | Why it failed |
|---|---|---|
| Exclusivity penalty fed back into the update loop (scoreboard row) | Flat: 0.33, 0.36, 0.24 (the `evaluation_history` of the run in `examples/c3-git-at-scale/exclusivity-20261015/`); after a dedicated feedback section, 0.35, 0.31, 0.33 (full C3 run, 1.43M tokens) | Reason truncated to 700 chars; loop drafts had sparse evidence. Within run-to-run noise. |
| LLM "exclusivity repair" (split / extract / merge / hybrid) | 14 of 24 proposals rejected (the repair entry of that run's `operation_log`). On the corrected measure every repair variant scored 0.34-0.44 against 0.38 without the feature (noise); the first apparent gain (0.23 -> 0.38) came partly from single-candidate dimensions. 31 -> 42 dimensions; judged orthogonality 0.70 -> 0.30 | Single-candidate dimensions are exclusive by construction and later dropped by selection. On C3 (5 sources, ~one system each) `min_candidate_decisions: 2` makes the LLM bundle unrelated mechanisms, and correct splits are blocked. Now off: `exclusivity_repair: bool = False` (`src/taxonomy_generator/settings.py:185`). |
| Coalesce values always adopted together | C3: per this session's offline simulation, 94 of 130 and 122 of 131 such pairs were single-source; C1/C2 had only 6 and 3 | Produces per-system bundles. |
| Split into never-co-adopted groups (colour the co-adoption graph) | 0 of 25 C1/C2 low-exclusivity dimensions partitionable with >= 2 candidates per part | No clean partition exists. |
| A "choose several" dimension kind | Rejected by the user (keep the notion of dimension; plan decision E5) | Changes the notion of dimension. |

The signal that did work: in C1/C2, several sources share the same *combination* of a dimension's values
(C1 45% of sources, C2 59%, C3 0%), and combinations often nest ({x} subset of {x, y}: C1 48%, C2 69%)
(`docs/plans/2026-10-15-feat-value-recoding-plan.md`, Evidence table). Recurring, nested combinations mean the
values are parts or degrees of one approach, not alternatives.

## Guidance

### 1. Recode values; do not restructure dimensions

`recode_values` (`src/taxonomy_generator/nodes/value_recoding.py:185-268`) runs after evidence linking in
`consolidate_values` (`src/taxonomy_generator/nodes/value_consolidator.py:214-217`, helper at `:231-246`). It is on
by default: `value_recoding: bool = True` (`src/taxonomy_generator/settings.py:193`).

**Select deterministically** (`value_recoding.py:200-207`). Thresholds in `settings.py:194-199`:

```python
row = dimension_exclusivity(c)
if row["score"] is None or row["score"] >= min_exclusivity or row["units"] < min_sources:
    continue
share = recurring_share(c)
(selected if share >= min_recurring else cause_ii).append(...)
```

Defaults: exclusivity < 0.8, >= 3 adopting sources, >= 0.3 of sources on a combination another source shares.
Dimensions failing only the last test are logged as `likely_cause_ii` and left alone.

**Propose** with one structured LLM call per dimension (`propose`, `value_recoding.py:224-233`). The payload lists
the adoptable values and every observed combination keyed `C1`, `C2`, ... with its sources and up to 2 excerpts
(`_combo_keys` / `_payload`, `:61-83`). The output (`RecodingOutput`, `src/taxonomy_generator/schemas.py:266`) has
new values with `includes` (old value ids as facets), one assignment per combination, or `keep`.

**Validate deterministically** (`validate`, `value_recoding.py:96-150`):

- >= 2 new values, no more than the old ones (`:107-110`);
- every old value included somewhere; no unknown ids (`:111-117`);
- every combination assigned exactly once, to a value whose facets contain the whole combination (`:121-129`);
- facet sets must differ; nested levels are allowed (`:134-139`);
- fit >= `min_fit` (`:140-144`); fit is the share of sources whose combination equals the facets of their value
  (`fit`, `:86-93`);
- every new value adopted by >= `min_sources_per_value` sources (`:145-149`), which blocks per-source bundles.

On failure, one retry with the errors (`RETRY_NOTE`, `:46`; loop at `:238-247`).

**Apply** (`apply`, `value_recoding.py:153-182`). Evidence is rebuilt from the assigned sources' passages only
(`:166-168`). Old values become `includes` (`:174-175`). Values no source adopts (rejected-only) keep their place
(`:177-180`). Declared hybrids are dropped because they name old ids (`:181`).

### 2. Measurement rules

The measure is in `src/taxonomy_generator/evaluation/exclusivity.py`.

- **Unit and adoption.** A unit is a source (or a system, via `unit_from_system_map`, `:198-203`). Only accepted
  stances count; rejections never count (`adopting_docs`, `:38-47`).
- **Score.** Share of adopting units that adopt exactly one candidate value. A declared hybrid adopted exactly
  counts as one choice (`dimension_exclusivity`, `:79-83`).
- **Exclude degenerate dimensions.** Leave out dimensions with fewer than `min_units` adopters or fewer than two
  candidate decisions (`taxonomy_exclusivity`, `:115-119`). Otherwise single-option dimensions inflate the score.
  Without this exclusion, the repair's single-option dimensions looked like a gain.
- **Always pair exclusivity with generality.** `generality` is the share of adopted values adopted by >= 2 units
  (`:190-195`); `fragmentation` reports dimensions and single-candidate dimensions (`:127-133`). Exclusivity alone is
  gamed by splitting or by per-source bundles.
- **The recurring-combination signal.** `value_combinations` (`:168-180`) and `recurring_share` (`:183-187`) drive
  selection.
- **A/B by replay, not by full runs.** `benchmark/replay_consolidation.py` replays a saved run from consolidation
  onward (`--set value_recoding=false|true`), so mining variance is removed. One full run per setting is within
  noise: judged orthogonality was 0.30 / 0.60 / 0.30 on near-identical taxonomies (exclusivity plan, Results).
- **Match with an independent model.** Use `--matching-llm openai/gpt-5.4-mini`, not the generator. With the
  generator (`gpt-5.6-luna`) as matcher, C1 looked +0.05; with the independent matcher it was neutral.
- **Apply the dimension cap at selection.** Giving the cap to the generation prompts forced broad topics (196 values
  in 5 dimensions). Now `cap_stage: str = "selection"` (`settings.py:179`).

## Why This Matters

Recoding raises exclusivity without new dimensions and without losing evidence. Replays on the saved 10-02 runs,
independent matcher (`docs/plans/2026-10-15-feat-value-recoding-plan.md`, "Independent matcher and a repeat"):

| | Excl. | Generality | Values | Option F1 (paper) | Decision F1 |
|---|---|---|---|---|---|
| C1 off | 0.45 | 0.84 | 117 | 0.50 | 0.76 |
| C1 on / on2 | 0.65 / 0.65 | 0.87 / 0.85 | 107 / 112 | 0.47 / 0.54 | 0.73 / 0.70 |
| C2 off | 0.70 | 0.71 | 56 | 0.25 | 0.42 |
| C2 on / on2 | 0.87 / 0.90 | 0.76 / 0.82 | 52 / 48 | 0.29 / 0.30 | 0.53 / 0.53 |

Exclusivity and generality rise in every replay; value counts fall. Expert-option coverage improves in C2 and is
about neutral in C1. Exact-name recall drops in C1 (0.47 -> 0.30 and 0.37) and is flat in C2, because values are renamed as alternatives.

C3 is safe. With the guards on, no dimension was eligible and nothing changed (9 flagged as likely cause (ii)). With
the guards relaxed (negative control), 4 of 20 dimensions became broad per-system "styles" (fit 0.36).

## When to Apply

- Sources adopt several values of one dimension, *and* several sources share the same combination. That is
  cause (i).
- Low exclusivity with no recurring combinations is cause (ii) or a small-corpus effect. Do not recode; report it.
  Small corpora where each source describes about one system (C3) fall here.
- Any time you report exclusivity: report generality and fragmentation next to it. Compare settings by replay with
  an independent matcher.
- Do not reach for loop penalties or LLM split/merge repair to fix exclusivity. Both were tried and stayed within
  noise.

## Examples

### A recoded C2 dimension

Per this session's C2 replay (`on`), "Reward-Hacking Detection Methods" (14 adopting sources, fit 0.71).

Before: three values that sources combine.

- Multiple complementary monitoring metrics
- Cross-metric degradation monitoring
- Cross-context behavioral evaluation

After: three nested levels, each an alternative answer that includes the old values as facets.

| New value | `includes` | Sources |
|---|---|---|
| Multi-metric monitoring | Multiple complementary monitoring metrics | s01, s11, s12, s13, s25, s29 |
| Cross-metric consistency monitoring | + Cross-metric degradation monitoring | s02, s04, s08, s18, s24 |
| Contextual behavioral assurance | + Cross-context behavioral evaluation | s06, s14, s27 |

Each source now takes one value. Two values with no adopting source ("Fabricated monitoring rationales",
"Subtle cheating detection") were left as they were.

### The guard that rejected nested levels

The first guard required "a facet of its own per alternative" (recoding plan, Results, line 128). It rejected the
example above: "Multi-metric monitoring" has no facet that the next level lacks. Nested levels are exactly what
recoding is for.

The replacement is two checks (`value_recoding.py:134-144`):

```python
seen: Dict[frozenset, str] = {}
for v in proposal.values:  # nested alternatives (levels: {x} and {x, y}) are fine; identical ones are not
    facets = frozenset(includes[v.key])
    if facets in seen:
        problems.append(f"new values {seen[facets]} and {v.key} include the same facets: alternatives must differ")
    seen.setdefault(facets, v.key)
f = fit(dim, proposal)
if f is not None and f < min_fit:
    problems.append(... "the alternatives are too broad; define them closer to the combinations the sources adopt")
```

"Facet sets must differ" rejects duplicates. The fit threshold rejects broad, overlapping bundles. The unit test
`test_guards_against_shared_facets_and_broad_alternatives` (`tests/unit_tests/test_value_recoding.py:135-148`)
covers all three cases: identical facets rejected, nested levels accepted, a broad proposal (fit 2/3) rejected at
`min_fit=0.8` and accepted at 0.5. In this session's C2 replay, fit rejected dimensions 3 and 10 on both attempts (fit 33% / 33%
and 10% / 30%), so they kept their values.

## Related

- [embedding-proposes-llm-judge-decides-ground-truth-matching.md](embedding-proposes-llm-judge-decides-ground-truth-matching.md): the matching LLM as its own, independent role; the replays here are a concrete case (the generator as matcher favoured the recoded values).
- [taxonomy-evaluation-suite-scoreboard-and-consistency.md](taxonomy-evaluation-suite-scoreboard-and-consistency.md): the scoreboard that the computed "Value exclusivity" row extends.
- [llm-dimension-relations-reversed-direction-and-split-fan-out.md](../logic-errors/llm-dimension-relations-reversed-direction-and-split-fan-out.md): the same lesson for relations; LLM structural proposals need deterministic validation, and prompt rules alone did not fix them.
- Plans: `docs/plans/2026-10-15-feat-value-exclusivity-plan.md` (measure, repair, loop feedback, results) and `docs/plans/2026-10-15-feat-value-recoding-plan.md` (recoding, guards, replays, how to reproduce). Concepts: Value Exclusivity and Value Recoding in `CONCEPTS.md`.
