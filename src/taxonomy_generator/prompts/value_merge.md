# Instruction

## Context

- **Goal**: Adjudicate one **borderline value-merge pair**. Two candidate values within the *same* dimension of a taxonomy sit just beyond the automatic embedding-distance merge threshold. Decide: are they the same decision, or genuinely different decisions along the dimension?

- **Use case**: {use_case}

- The use case is the yardstick: two labels are "the same decision" only if merging them preserves the distinctions the use case cares about.

## Dimension

{dimension_json}

## Candidate Values

- **Value A**: {value_a_json}
- **Value B**: {value_b_json}

## Decision Rules

- Say **same decision** when the two values name interchangeable positions along the dimension — merging them loses nothing relevant to the use case.
- Say **different decisions** when each value captures a distinct position that the use case might need to distinguish (even if they are related).
- Do not be fooled by surface wording: identical wording can still name different decisions if their supporting evidence differs; different wording can name the same decision.
- When uncertain, prefer keeping them separate (different decisions) — over-merging loses information.

## Output

- `same_decision`: your verdict.
- `rationale`: why, judged against the use case.

Output in **English** only.