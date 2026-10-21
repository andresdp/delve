# Instruction

## Context

- **Goal**: Check **theoretical saturation** — decide whether the open codes from the current minibatch are already subsumed by the existing taxonomy's dimensions, or whether they reveal genuinely new concepts the taxonomy does not yet capture.

- **Use case**: {use_case}

- "Uncovered" means uncovered *relative to the design space's goals*: a concept only counts as uncovered when it matters to the stated use case and no existing dimension's axis of variation could absorb it.

## Existing Taxonomy

{taxonomy_json}

## Open Codes from the Current Minibatch

{codes_json}

## Decision Rules

- A code is **covered** when at least one dimension's name or description captures the concept it names — the dimension's axis of variation subsumes it as a value or a position along that axis.
- A code is **uncovered** when no existing dimension could absorb it without conflating two different axes.
- Judge against the use case: codes irrelevant to the design space are covered-by-definition (ignore them).
- Be conservative: only report uncovered concepts when the evidence is clear. Spurious gaps cause churn; missed gaps cause under-coverage.

## Output

- `is_saturated`: true when every relevant open code is covered.
- `uncovered_concepts`: the labels of uncovered codes (empty when saturated).
- `rationale`: your verdict's justification, relative to the use case.

Output in **English** only.