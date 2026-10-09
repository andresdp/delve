# Instruction

## Context

- **Goal**: Review a finished design-space taxonomy and find dimensions that are **parts of one design decision**. A practitioner would document each such group as a single architectural decision, with the values of all its dimensions as the alternatives.

- **Use case**: {use_case}

- A dimension is one design decision (an axis); its values are the alternative options for that decision.

## Taxonomy

{dimensions_json}

## Decision Rules

- Group dimensions when a practitioner makes **one** choice that settles them together: one dimension is a facet, parameter or sub-step of the other's choice, or both name the same decision at different levels of detail.
- Keep dimensions separate when they are choices a practitioner makes **independently**, even when they share a topic. *How to detect* a problem and *how to mitigate* it are different decisions; so are *what to monitor* and *how to respond to an alert*.
- Judge by the values: merge only when the merged dimension's values would still be alternatives for one question.
- When uncertain, keep them separate: merging two real decisions loses information.
- A dimension belongs to at most one group. Most dimensions should stay as they are.

## Output

- `groups`: one entry per group of at least two dimension ids (the first id is kept), with the shared `question`, a `name` and `description` for the merged dimension, and the `reason`. An empty list when nothing should merge.

Output in **English** only.
