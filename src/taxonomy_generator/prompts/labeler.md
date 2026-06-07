# Instruction

## Context

- **Goal**: Classify a document into the single most relevant category from the provided taxonomy.
- **Use case**: {use_case}

## Taxonomy

{taxonomy_json}

## Steps

1. **Read** the document carefully, identifying its main topic, intent, or theme.

2. **Match** the document to the single best-fitting category from the taxonomy above. Consider both the category name and description when making your choice.

3. **Score** your confidence in the match:
   - **1.0** — Perfect fit. The document clearly and unambiguously belongs to this category.
   - **0.7–0.9** — Good fit. The document matches well but has minor secondary themes.
   - **0.4–0.6** — Partial fit. The document could belong to this category but also fits others, or only partially matches.
   - **0.1–0.3** — Poor fit. The document doesn't match any category well; this is the closest option.
   - **0.0** — No fit at all (should only occur with the fallback category).

4. **Reason** — Briefly explain why you chose this category and your confidence level.

## Rules

- Choose **exactly one** category per document.
- If no category fits the document well, use the fallback category: **{fallback_category}**.
- The category name in your response must **exactly match** a category name from the taxonomy.