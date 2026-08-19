# Instruction

## Context

- **Goal**: Classify a document into the single most relevant category from the provided taxonomy. When the chosen category lists specific **values** (decisions along its axis), also pick the single best-fitting value — two-level labeling.
- **Use case**: {use_case}

## Taxonomy

{taxonomy_json}

## Steps

1. **Read** the document carefully, identifying its main topic, intent, or theme.

2. **Match** the document to the single best-fitting category from the taxonomy above. Consider both the category name and description when making your choice.

3. **Match the value** — when the chosen category lists specific **values** (decisions along its axis), pick the single best-fitting value id from that category. Choose `null` when the category has no values or none of them fit.

4. **Propose when none fit** — when the chosen category HAS values but NONE of them fit the document's specific decision, set `value_id` to null and write a concise `proposed_value_label` (2–6 words) naming that decision so it could become a new value on the category's axis.

5. **Score** your confidence in the match:
   - **1.0** — Perfect fit. The document clearly and unambiguously belongs to this category.
   - **0.7–0.9** — Good fit. The document matches well but has minor secondary themes.
   - **0.4–0.6** — Partial fit. The document could belong to this category but also fits others, or only partially matches.
   - **0.1–0.3** — Poor fit. The document doesn't match any category well; this is the closest option.
   - **0.0** — No fit at all (should only occur with the fallback category).

6. **Reason** — Briefly explain why you chose this category (and value, when applicable) and your confidence level.

## Rules

- Choose **exactly one** category per document.
- If no category fits the document well, use the fallback category: **{fallback_category}**.
- The category name in your response must **exactly match** a category name from the taxonomy.
- The value id in your response (when not null) must **exactly match** a value id listed under the chosen category.
- `proposed_value_label` must be null when `value_id` is set, when the chosen category has no values at all, and when the fallback category **{fallback_category}** was used.
