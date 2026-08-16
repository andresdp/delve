# Instruction

## Context

- **Goal**: Perform **selective coding as use-case relevance filtering** — select the subset of reviewed taxonomy dimensions that matter for the stated use case. Dropped dimensions are *not deleted*: they remain part of the full taxonomy and are kept inspectable with a rationale.

- **Use case**: {use_case}

- The use case is the **entire basis** for this step. A dimension is relevant only when knowing a document's position along its axis would change a decision, analysis, or action within the use case.

## Reviewed Taxonomy

{taxonomy_json}

## Decision Rules

- **Select** a dimension when classifying documents along it directly serves the use case.
- **Drop** a dimension when it is well-formed but orthogonal to the use case's goals — describing it as irrelevant to the use case in the rationale.
- Be conservative about dropping: only drop when you can articulate why the dimension cannot affect the use case.
- Do not restructure, rename, merge, or split dimensions here — this step only filters.

## Output

- `selected_ids`: ids of relevant dimensions, in order of relevance.
- `dropped`: for every dropped dimension, its id and a rationale. Never silently omit a dropped dimension.
- `rationale`: overall reasoning for the selected subset.

Output in **English** only.