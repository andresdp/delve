# Instruction

## Context

- **Goal**: Check one dimension of a finished design-space taxonomy. Each of its values should be an alternative answer to **this dimension's question**. Find the values that answer a different question, and the values that are not options at all.

- **Use case**: {use_case}

- A dimension is one design decision (an axis); its values are the alternative options for that decision.

## Decision point under review

{dimension_json}

## Other dimensions of the taxonomy

{other_dimensions_json}

## Decision Rules

- `keep` a value that is an alternative answer to the dimension's question. Most values should be kept; you may leave them out of the output.
- `move` a value that is an alternative answer to **another** dimension's question listed above. Give that dimension's id in `to_dimension_id`. Move only when the other dimension is clearly the better home.
- `outcome` a value that is not an option for any decision: a goal, a principle, a quality attribute, or an effect of a choice.
- When uncertain, keep the value where it is.

## Output

- `values`: one entry per value to move or turn into an outcome (`value_id`, `action`, `to_dimension_id` — empty string unless moving — and a one-sentence `reason`). An empty list when every value fits.

Output in **English** only.
