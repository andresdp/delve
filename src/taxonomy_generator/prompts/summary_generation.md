Your task is to compress a piece of text by extracting information relevant to a specific use case.

## Context

- **Use case**: {use_case}

## Guidelines

- **Summary**: Extract and compress the key information from the text that is relevant to the use case above, in {summary_length} words or fewer. Omit details unrelated to the use case. Focus on aspects that would help classify or categorize this text.
- **Explanation**: Briefly explain the main themes, topics, or intents that connect this text to the use case, in {explanation_length} words or fewer.

You must respond with a JSON object containing:
- "summary": your contextual summary
- "explanation": your explanation of relevance to the use case