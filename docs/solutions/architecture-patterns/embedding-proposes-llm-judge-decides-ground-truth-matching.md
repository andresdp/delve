---
title: "Scoring a Generated Design Space Against Expert Ground Truth: Embeddings Propose, a Validated LLM Judge Decides"
date: 2026-10-04
category: architecture-patterns
module: evaluation
problem_type: architecture_pattern
component: service_layer
severity: medium
applies_when:
  - "Scoring an LLM-generated taxonomy (dimensions with candidate values) against an expert ground truth of design decisions with options"
  - "Tempted to declare matches from embedding distance alone or to tune a distance threshold on expert-vs-expert pairs"
  - "Choosing or changing the matching LLM judge, whose choice moves the reported scores"
  - "Reporting option P/R/F1 or decision alignment across ground-truth views that share elements"
tags: [ground-truth-matching, llm-judge, embedding-distance, graded-labels, judge-sensitivity, evaluation-frame, jaccard-matching, taxonomy-generator]
---

# Scoring a Generated Design Space Against Expert Ground Truth: Embeddings Propose, a Validated LLM Judge Decides

## Context

Delve's SANER 2027 evaluation scores an LLM-generated design space against expert ground truth. The generated design space is a DelveDSpace taxonomy: dimensions whose values are candidate design decisions. The ground truth is the architectural design decisions and options of studies C1 (ML workflow) and C2 (RL monitoring), each with a paper view and a model view. The question is when a system value counts as the same thing as an expert option.

The first plan was to embed both sides and apply a distance cutoff. On these studies that does not work. Embedding distance is useful only for proposing candidate pairs, and an LLM judge has to decide them. The judge also changes the scores, so the judge model must be fixed in advance, recorded, reported with its sensitivity, and checked against human gold labels. This work is on branch `feat/ground-truth-matcher` (unmerged as of this writing). The command is:

```bash
python main.py --match-gt <taxonomy.json> --gt benchmark/<study>/gt --config <yaml> \
  [--matcher-mode embeddings] [--matching-llm openai/gpt-5.4-mini]
```

## Guidance

**1. Use one serialization on both sides, and let embeddings only propose and bound pairs.** Both items are rendered as `"<decision or dimension> › <option or value>: <description>"` with CamelCase names split (`src/taxonomy_generator/evaluation/gt_match.py:164-175`). They are compared by cosine distance, `1 - cos` clipped to [0, 2] (`gt_match.py:397-400`). In judge mode, a distance only decides two things: whether a pair is far enough away to be called `different` without a judge call, and whether a borderline pair is close enough among nearest neighbours to be worth a judge call:

```python
# gt_match.py:448-458
if config.lower_threshold > 0 and d <= config.lower_threshold:  # 0 disables auto-"same"
    record["label"] = "same"
elif d > config.upper_threshold:
    continue  # far apart: "different" without the judge
elif j not in near_sys[i] and i not in near_opt[:, j]:
    record["label_source"] = "auto_rank"
else:
    ...  # seeded order, queued for the judge
```

The defaults are `lower_threshold: 0.0`, `upper_threshold: 0.60` and `max_candidates: 5` (`src/taxonomy_generator/settings.py:285-290`). With a lower threshold of 0, every `same` label comes from the judge.

**2. Derive thresholds from ground-truth-only data, before seeing any system scores.** `benchmark/frame_thresholds.py` embeds every attached option with the matcher's serialization. It then reports two distance distributions:

- distinct options within the same study: no `same` label should ever join two of these;
- options from different studies: these are unrelated.

It also prints the closest distinct pairs (`benchmark/frame_thresholds.py:46-68`). Thresholds are frozen in `benchmark/README.md` under "Evaluation frame" (`benchmark/README.md:144-169`). Any change made after scores were seen goes in a dated "Changes after scores were seen" log, with the reason (`benchmark/README.md:187` onwards).

**3. Use graded labels and record where every label came from.** The judge answers one of `same/broader/narrower/related/different`. Only `same`, `broader` and `narrower` count as hits (`gt_match.py:55-56`). Every pair records a `label_source`:

- `auto`: beyond the upper threshold;
- `auto_rank`: borderline, but outside both items' nearest neighbours;
- `judge`: labeled by the judge;
- `embedding`: labeled in embeddings-only mode.

The sources are defined at `gt_match.py:422-425` and `gt_match.py:508`, and the match file records the counts (`gt_match.py:512-514`, `gt_match.py:695`). This keeps a pair that was never judged distinguishable from a pair the judge called wrong (`benchmark/README.md:171-177`).

**4. Present each pair blind, in a seeded order, and orient the answer afterwards.** The judge sees "Item 1" and "Item 2" and is never told which side is the ground truth (`gt_match.py:278-286`). The order is seeded per pair (`gt_match.py:455-457`). Because "broader" and "narrower" are relative to the item order, they are flipped back to the system value's point of view:

```python
# gt_match.py:289-293
def orient_label(label: str, order: str) -> str:
    if order == "gt_first":
        return {"broader": "narrower", "narrower": "broader"}.get(label, label)
    return label
```

The judge instructions tell it to compare the options themselves and ignore which decision each one sits under (`gt_match.py:62-64`). Placement is scored separately. The cache key is built from the judge model, `JUDGE_VERSION` (a hash of the instructions) and the ordered texts (`gt_match.py:74`, `gt_match.py:376-378`). So editing the instructions or changing the judge invalidates the cache, but reruns with the same settings stay deterministic. If the judge returns a label outside the five allowed, it is retried once, then recorded as `different` with a warning (`gt_match.py:331-342`).

**5. Treat the matching LLM as its own role, keep it independent, and record it.** The project has three LLM roles: `generation_llm`, `evaluation_llm` and `matching_llm` (`settings.py:33-54`). If two roles use the same model, the matcher logs a warning and writes it to the outputs as `llm_warnings`. It does not stop the run (`gt_match.py:153-159`, `gt_match.py:774-776`, `gt_match.py:806`). Every output also includes the full matcher config and `judge_version` (`gt_match.py:130-132`). (The `MatcherSettings` docstring at `settings.py:277-278` still says the judge "must be" a different model; actual behavior is warn-only.)

**6. Report one-to-one Jaccard alongside P/R/F1.** Precision and recall count values and options independently. One generic value that hits many options improves recall without being penalized. `matching_size` computes a maximum one-to-one matching with `linear_sum_assignment`, and Jaccard is calculated on that matching (`gt_match.py:593-611`, `gt_match.py:645-651`). Embeddings-only mode applies the same restriction when assigning `same` labels (`gt_match.py:496-501`).

**7. Give each shared element the same text in every view, and record which text was used.** An element that appears in both views takes its text from the first view in `VIEW_TEXT_PRECEDENCE = ("paper", "model")` (`gt_match.py:222-266`). The order is written to every output as `gt_text_precedence` (`gt_match.py:810`). As a result, paper-view and model-view metrics differ only in scope, meaning which elements count, and never in wording (`benchmark/README.md:117-125`). Wording sensitivity is planned as a separate experiment, E12.

**8. Make each view's metric pools consistent with that view's own alignment.** Metrics are computed per view, but some exclusions come from the union of both views. Whatever a view keeps in its numerator must also stay in its denominator:

```python
# gt_match.py:656-662
outside = {d for d in dim_ids
           if any(dim == d for dim, _ in union_alignment["lenient"])
           and all(dec not in view_decs for dim, dec in union_alignment["lenient"] if dim == d)}
# A dimension aligned within the view stays in its pool (lenient covers strict), so precision <= 1.
outside -= {d for d, _ in alignment["lenient"]}
```

## Why This Matters

- **A distance cutoff mislabels matches without any error.** Among expert options, the closest distinct pairs are opposite choices under the same decision. The shared decision prefix dominates the embedding, so any cutoff that admits true matches also merges opposites.
- **Calibration does not carry over from expert pairs to system pairs.** A threshold fitted on expert-vs-expert pairs does not apply to system-vs-expert pairs, because the system words things differently.
- **The judge choice can move the headline numbers by about 0.2 F1.** If the judge is not recorded and validated, the result describes the judge as much as the system.
- **Unrecorded label sources hide missed matches.** Without them, unjudged pairs count as true negatives, and candidate recall (how many true matches the automatic labels miss) cannot be measured.
- **Inconsistent per-view pools produce impossible values.** Before the fix, paper-view decision precision could exceed 1 (per this session's code review; fixed and covered by a regression test).

## When to Apply

- Scoring any generated taxonomy, design space, or concept list against an expert reference when the two sides use different vocabulary.
- Any setup where items carry a shared parent prefix (decision, category, topic) that dominates the embeddings.
- Adding a new matcher mode, judge, threshold, or ground-truth view. Before scoring, update the evaluation frame and the change log.
- Computing metrics per subset (view, study, split) when some exclusions come from the union of subsets.

## Examples

**Threshold derivation (ground truth only, `text-embedding-3-small`, 184 attached options for C1 and C2, 2026-10-03):**

| Pair population | min | p1 | p2 | p5 | median |
|---|---|---|---|---|---|
| Distinct options, same study | 0.031 | 0.177 | – | 0.326 | 0.611 |
| Options of different studies (unrelated) | 0.416 | 0.564 | 0.600 | 0.650 | – |

The closest distinct pairs are opposites: "No AutoML" vs "AutoML" at 0.031, "Batch-based" vs "Real-time" processing at 0.047, and "MLOps" vs "No MLOps" at 0.069. Because of this, `lower_threshold` is 0, and `upper_threshold` is 0.60, the 2nd percentile of unrelated pairs (`benchmark/README.md:158-169`).

**Embeddings-only mode found zero matches.** It used `same_threshold: 0.18` (`settings.py:304`), the 1st percentile of distinct expert pairs, chosen before any embeddings-only score was seen. On both 2026-10-02 runs, every metric is 0. For C1, see `examples/c1-ml-workflow/c1-ml-workflow_20261002_185546_emb_gt_metrics.json`.

- Every system value is at least 0.21 from its nearest expert option.
- The judge's labels overlap almost entirely in distance. On C1, `same` has a median of 0.44 (range 0.21-0.58), `related` 0.49 and `different` 0.52.
- The threshold was deliberately **not** retuned on these scores, because that would fit it to the outcome (`benchmark/README.md:189-206`).

**Judge sensitivity on the same runs and frame, `gpt-5.4-mini` vs `gpt-5.6-luna`.** Values come from `examples/<case>/*_gt_metrics.json` and `examples/<case>/gt_luna/*_gt_metrics.json`:

| Metric (paper view) | gpt-5.4-mini | gpt-5.6-luna |
|---|---|---|
| C2 option F1 (recall) | 0.22 (0.18) | 0.43 (0.40) |
| C1 option F1 | 0.50 | 0.58 |
| C1 exact (`same`-only) recall | 0.47 | 0.14 |
| C1 decision F1, strict | 0.76 | 0.67 |
| C2 decision F1, strict | 0.35 | 0.35 |

- Of C1's 824 judged pairs, luna answered `same` 21 times, against 63 for gpt-5.4-mini. It shifted those pairs to `broader`, `narrower` and `related`.
- On C2, decision-level F1 did not change while option-level F1 doubled (on C1 both moved by under 0.1).
- Luna also generated both runs, so its scores carry `llm_warnings` saying the matching is not independent of the generation (`benchmark/README.md:219-231`).
- Some `broader` hits are generous. For example, `gpt-5.4-mini` judged "Multiple complementary monitoring metrics" broader than "Human Review" (luna called it `related`). The lenient hit definition therefore needs validation against human gold labels (A6) before it is reported.

**Per-view precision-pool bug, before and after.** Previously, the set of dimensions excluded from a view's pool (`outside`) was computed only from the union alignment. A dimension aligned within the paper view could be counted in the numerator while being excluded from the denominator, `dim_pool`, so paper-view decision precision could exceed 1. The fix is the single line `outside -= {d for d, _ in alignment["lenient"]}` (`gt_match.py:659-660`). A regression test now covers it.

## Related

- [taxonomy-evaluation-suite-scoreboard-and-consistency.md](taxonomy-evaluation-suite-scoreboard-and-consistency.md):
  same evaluation subsystem. Its consistency comparison aligns dimensions *between runs of the same system*
  with a distance threshold plus judge adjudication of a borderline band. The finding here, that distance
  cannot separate same from different design options and that a threshold calibrated on one distribution
  does not transfer to another, is a caveat for reusing that pattern across systems or against experts.
- [deepeval-geval-temperature-unsupported-on-newer-openai-models.md](../integration-issues/deepeval-geval-temperature-unsupported-on-newer-openai-models.md):
  the matcher's judge is a deepeval model built through the same shared factory (`src/taxonomy_generator/evaluation/judge.py`,
  temperature 1.0).
