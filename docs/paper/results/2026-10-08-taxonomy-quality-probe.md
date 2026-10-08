# Taxonomy quality probe: dimension focus and evidence links (2026-10-08)

**Question.** The first C3 run showed values that are not options, dimensions that mix decisions, and doubtful evidence links. Are these specific to C3, or general? The answer decides whether general pipeline fixes are worth making before the freeze.

**Runs.** The latest tools-mode run of each case, i.e. the update strategy of the study configs:

| Case | Run |
|---|---|
| C1 | `examples/c1-ml-workflow/u7/c1-u7b-tools_taxonomy_20261005_122709.json` |
| C2 | `examples/c2-rl-monitoring/u7/c2-u7b-tools-norelevance_taxonomy_20261005_110747.json` (no relevance filter, as in the current config) |
| C3 | `examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350.json` (first C3-raw run) |

**Method.** `benchmark/quality_probe.py`, judge `openai/gpt-5.4-mini`, a different model from the generator `gpt-5.6-luna`.
- **Dimension audit:** one call per selected dimension. It states the dimension's design question, then classifies each value as `option`, `fact`, `effect`, `goal`, or `other_question` (a genuine choice, but for a different question).
- **Evidence-link check:** 40 value → passage links per run, seed 7, stratified by status (accepted 16, mixed 8, rejected 8, outcome 8). Each link gets `supports`, `partial` or `unrelated`, judged against the passage text.
- **Outputs:** `examples/<case>/probe/`. The values and links sheets have an empty `human` column for spot-checks.
- **Not validated:** the labels are an unvalidated LLM judge. An author spot-check of the 39 non-option labels on C3 agreed with most of them; a few were borderline (e.g. rack-at-a-time maintenance). Rates are estimates. With 8 links per status, per-status link rates are rough.

## Results

A dimension is **focused** when none of its candidate values (accepted, mixed, rejected) answers another question. Outcome values are left out, because the pipeline keeps them on a dimension on purpose.

| | C1 | C2 | C3 |
|---|---|---|---|
| Dimensions | 30 | 19 | 22 |
| Focused dimensions | 20% | 47% | 55% |
| Candidate values that are options | 63% | 77% | 70% |
| … answer another question | 26% | 20% | 22% |
| … are facts, effects or goals | 12% | 3% | 8% |
| Links: supports / partial / unrelated | 70 / 30 / 0% | 63 / 20 / 18% | 85 / 10 / 5% |
| Accepted links: supports / unrelated | 67 / 0% | 81 / 0% | 81 / 6% |
| Mixed links: supports / unrelated | 75 / 0% | 13 / 38% | 100 / 0% |

**C3 only (via B7, primary system).** 12 of 22 dimensions hold candidate values from two or more systems. The other 10 belong to one system: four are Spokes operations (maintenance, failure recovery, checksums, update scheduling) and six are Scalar client details.

## Reading

1. **The main general problem is bundled decisions.** In every case, a fifth to a quarter of the candidate values answer a different design question than their dimension. Most dimensions are not focused, and C1 is the worst (24 of 30). C3 examples:
   - "Authority Synchronization" collects most of what Continuity does: storage tier, primary ownership, consistency.
   - "Replica Failure Recovery" mixes failure detection with recovery.

   This affects:
   - decision-level alignment against the expert models (C1/C2);
   - the coherence of sampled design points;
   - C3 placement, because systems end up compared inside "their" dimension rather than on a shared axis.
2. **Values that are not options are a smaller issue:** 3–12% of candidates, mostly goals or principles labeled `accepted`.
3. **Evidence links are mostly sound.** Accepted links have no unrelated passage in C1 or C2 and 6% in C3. The weak spot is C2's `mixed` and `outcome` links, with 38% unrelated each (small samples). Mixed values come from merging stances (`merge_value_stances`), which pools the links of merged values. The attested design points of C3 also rest on these links (see the C3 README).

## Implication for step 2 (general fixes, validated on C1/C2)

- **Highest value:** a decision-focus pass after consolidation. For each dimension, values that answer another question move to the dimension that answers it, or form a new dimension. Facts and goals are relabeled or dropped.
  - **Validation:** re-run the probe (focused rate up), and check that C1/C2 option F1 and decision alignment do not drop.
- **Lower priority:** tighter evidence links for merged (mixed) values.
- **Not changed:** the C3 corpus and the C3 config. The single-system dimensions partly reflect the corpus, which is reported as is.
