# Instruction

## Context

- **Goal**: Adjudicate one **candidate dimension-merge pair**. Two dimensions of a design-space taxonomy sit close together in embedding space. Decide: do they name the **same design decision**, so their values are alternatives for one decision, or **different decisions**?

- **Use case**: {use_case}

- A dimension is one design decision (an axis); its values are the alternative options for that decision.

## Candidate Dimensions

- **Dimension A**: {dimension_a_json}
- **Dimension B**: {dimension_b_json}

## Decision Rules

- Say **same decision** when a practitioner would make *one* choice that covers both dimensions, and their values are options for that one choice. Typical cases: the same decision under two names, or one dimension is a narrower wording of the other with overlapping options.
- Say **different decisions** when the dimensions are separate choices a practitioner makes independently, even if they share a topic. For example, *how to detect* a problem and *how to mitigate* it are different decisions. So are *what to monitor* and *how to respond to an alert*.
- Judge by the options: if merging would put options that answer different questions on one axis, they are different decisions.
- When uncertain, prefer keeping them separate (different decisions): merging two real decisions loses information.

## Output

- `same_decision`: your verdict.
- `rationale`: why, judged against the use case.

Output in **English** only.
