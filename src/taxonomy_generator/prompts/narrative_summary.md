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

- **Reword and synthesize only.** You are polishing existing text for readability, not analyzing new data. Every claim about taxonomy *structure* (dimensions, relations, values) must already be present, in substance, in the taxonomy explanation or a dimension description above. The use case (given verbatim above, not something you infer) is the one exception: state it directly, it is not a claim you are fabricating.
- **Never invent structure.** Do not introduce a dimension name, relation type, or value name that is not present in the "Dimensions" section above. Do not assert a relation between dimensions unless the source material already states it.
- **The "Dimensions" section is the sole authority on what exists in this view.** The "Taxonomy Explanation" text may have been written for an earlier or broader version of the taxonomy and can reference dimensions that are no longer part of this rendered view. Ignore any such reference — do not carry a dimension, relation, or value into your summary unless it also appears in "Dimensions".
- **Ground the summary in the use case.** Check whether the taxonomy explanation already makes clear what question or use case this taxonomy serves. If it does, no change needed. If it doesn't — or only implies it — open with a brief sentence stating the use case plainly, so a reader with no prior context knows why these particular dimensions were chosen before reading further.
- **Do not contradict the source.** If the explanation and a dimension description appear to disagree, preserve both framings rather than resolving the tension yourself.
- Write for a reader with no prior context on this taxonomy: prefer plain language over jargon, and spell out acronyms on first use if the source material does.
- Keep the summary to a few short paragraphs — long enough to orient the reader, short enough to read before the diagram.

## Output

Respond with a JSON object containing:
- `summary`: the narrative summary described above.

Output in **English** only.
