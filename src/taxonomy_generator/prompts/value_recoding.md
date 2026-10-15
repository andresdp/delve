# Instruction

## Context

- **Goal**: A dimension of a design space is a decision; its values should be **alternative answers** to the dimension's question, so that a system takes one value per dimension. The sources below adopt **combinations** of this dimension's values: several values at once. Usually that means the values describe **parts or degrees** of an approach rather than alternatives. Rewrite the values as alternatives, so that each source's combination corresponds to exactly one new value.

- **Use case**: {use_case}

## Dimension

{dimension_json}

## Combinations adopted by the sources

Each combination has a key, the current values it contains, the sources adopting exactly that combination, and short excerpts of their passages.

{combinations_json}

{retry_note}

## Rules

- Each new value is a **whole answer** to the dimension's question (for example a level or style of the approach: "ad-hoc metric logging", "experiment tracking", "metadata store with lineage"), named as a noun phrase. Do not name a value after a source, a company or a product unless the product is the option itself.
- `includes`: the current values each new value covers (its facets). Every current value listed in the dimension must be included in at least one new value; a current value may be included in several new values when it is part of several alternatives.
- `assignments`: assign **every** combination key to exactly one new value: the alternative that source combination represents. The new value must include every current value of that combination.
- Each new value must be the answer of **at least two sources** (through the combinations assigned to it). Prefer few, general alternatives over one value per source.
- Use at least two new values, and no more new values than the current candidate values.
- Set `keep` to true (and leave `values` and `assignments` empty) when the current values already are alternatives, or when the combinations show unrelated concerns that no set of alternatives can express.

## Output

- `keep`, `values` (`key`, `label`, `description`, `includes`), `assignments` (`combination`, `value_key`), and a short `rationale`.

Output in **English** only.
