# Instruction

## Context

- **Goal**: Repair one dimension of a finished design-space taxonomy whose values are **not alternatives**. A dimension is one design decision, and its values are the alternative answers to that decision's question, so a system should adopt **one** value per dimension. The evidence below shows sources (each describing a system) that adopt **several** values of this dimension at once. Decide why, and fix the dimension.

- **Use case**: {use_case}

## Dimension under repair

{dimension_json}

## Values adopted together

Each entry is a pair of values that the same sources adopt, with the sources and short excerpts of their passages.

{pairs_json}

## Other dimensions of the taxonomy

{other_dimensions_json}

{retry_note}

## Actions

Propose the fewest actions that make the dimension's values alternatives again, and keep the taxonomy compact: prefer moving values to existing dimensions over creating new ones. Each value id may appear in at most one action.

- `move`: values answer the question of **another existing dimension** listed above. Give their `value_ids` and that dimension's id in `to_dimension_id`. This is the first choice for a lone value that answers a different question.
- `split`: the dimension bundles several decisions. Give `parts`: every value of the dimension goes to exactly one part, each part has a name (the decision), a description (its question) and **at least two candidate decisions** (accepted, rejected or mixed values).
- `extract`: some values answer a **sub-question** (a mechanism or detail of how another option works). Give their `value_ids` (**at least two candidate decisions**) and the `name` and `description` of the new dimension; it becomes a sub-decision of this one.
- `merge`: two or more values are **the same option** at a different granularity or under different words. Give their `value_ids` and the merged `name` (the label).
- `outcome`: values that are a goal, a quality or an effect of a choice, not an option. Give their `value_ids`.
- `hybrid`: systems genuinely **combine** these values (both are used, by design, for the same decision). Give their `value_ids`. Use it sparingly: only when the excerpts show a deliberate combination, not when the values answer different questions.

When the values are alternatives and the sources only compare them or changed from one to the other over time, propose no action.

## Output

- `actions`: the actions (an empty list when none applies). Fill every field: `value_ids` (empty for `split`), `to_dimension_id` (empty unless `move`), `parts` (empty unless `split`), `name` and `description` (empty strings when unused), and a one-sentence `reason`.
- `rationale`: one or two sentences on why the sources adopt several values of this dimension.

Output in **English** only.
