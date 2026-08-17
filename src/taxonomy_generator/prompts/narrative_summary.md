# Instruction

## Context

- **Goal**: Write a short **narrative summary** for a grounded-theory report, read by collaborators who never ran the pipeline. It sits above a mermaid relationship diagram and a per-dimension catalog, and gives readers a plain-language overview before they dive into the structural detail.

- **Use case**: {use_case}

## Source Material

### Taxonomy Explanation

{explanation}

### Dimensions

{dimensions}

## Guidelines

- **Reword and synthesize only.** You are polishing existing text for readability, not analyzing new data. Every claim in your summary must already be present, in substance, in the taxonomy explanation or a dimension description above.
- **Never invent structure.** Do not introduce a dimension name, relation type, or value name that is not present in the "Dimensions" section above. Do not assert a relation between dimensions unless the source material already states it.
- **Do not contradict the source.** If the explanation and a dimension description appear to disagree, preserve both framings rather than resolving the tension yourself.
- Write for a reader with no prior context on this taxonomy: prefer plain language over jargon, and spell out acronyms on first use if the source material does.
- Keep the summary to a few short paragraphs — long enough to orient the reader, short enough to read before the diagram.

## Output

Respond with a JSON object containing:
- `summary`: the narrative summary described above.

Output in **English** only.
