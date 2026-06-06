# TnT-LLM: Text Mining at Scale with Large Language Models 🚀

## Overview

This project implements TnT-LLM, a framework designed for large-scale text mining using Large Language Models (LLMs). TnT-LLM automates two core tasks: label taxonomy generation and text classification, both of which traditionally require significant manual effort and domain expertise.

The framework consists of two phases:

**Taxonomy Generation**: A zero-shot, multi-stage process where LLMs automatically generate and refine a label taxonomy based on the input text data.

**Text Classification**: LLMs then generate pseudo-labels to train lightweight, scalable classifiers that can be deployed efficiently at scale.

TnT-LLM combines the accuracy of LLMs with the scalability of traditional classifiers, making it highly efficient for real-world applications such as conversational AI analysis. This project uses the framework to extract insights and organize unstructured text data with minimal human intervention.

For more detailed information, you can refer to the [original paper](https://arxiv.org/abs/2403.12173).

![TNT LLM Diagram](images/tnt_llm.png)

### 🔥 Why This Matters

Traditional text mining approaches often face two major challenges:
- **High Costs and Time Involvement**: Most existing methods rely heavily on **human annotators** and **domain experts** to manually generate taxonomies and classify text data. This process is slow, expensive, and prone to errors, making it difficult to scale for large datasets.
- **Limitations of Unsupervised Methods**: Unsupervised techniques like text clustering and topic modeling, while faster, lack the necessary **interpretability** and **guidance** to produce meaningful and actionable results. These methods often result in vague groupings that require manual review and adjustment.

**TnT-LLM** changes the game by leveraging the power of **Large Language Models** in a novel way:
- It **automates** both taxonomy creation and text classification, significantly reducing human involvement while maintaining accuracy.
- The framework uses a **zero-shot approach**, allowing LLMs to generate and refine label taxonomies without prior training, making it adaptable to a wide variety of use cases.
- By using LLMs to generate **pseudo-labels**, TnT-LLM allows lightweight classifiers to be trained and deployed at scale, offering a **balance between scalability and accuracy** that traditional methods struggle to achieve.

This approach unlocks the ability to apply LLMs effectively to large-scale text mining problems with minimal overhead, transforming how we extract insights from unstructured text data.


### 🔍 Key Features:
- **Automated Taxonomy Generation**: Quickly and accurately create label taxonomies without the need for human annotators or domain experts.
- **LLM-Augmented Text Classification**: Use LLMs to generate pseudo-labels, enabling lightweight classifiers to handle large-scale text data efficiently.
- **Scalable Processing of Large Text Corpora**: Designed to handle vast amounts of data, ensuring performance and accuracy even at scale.
- **Optimized for Accuracy and Efficiency**: Balances the powerful capabilities of LLMs with the scalability and transparency of traditional classifiers, delivering high performance without compromising speed.


## 🌟 Use Cases

TnT-LLM enables powerful and scalable applications in text mining and analysis:

1. **User Intent Detection**: Leverage TnT-LLM’s zero-shot, multi-stage taxonomy generation to identify user intent in conversations without extensive domain-specific training.
2. **Content Categorization**: Automatically generate and refine taxonomies for organizing large-scale document collections, ensuring scalability and accuracy.
3. **Trend and Theme Detection**: Detect emerging trends with greater precision than traditional clustering, thanks to LLM-augmented classification.
4. **Academic Research Assistance**: Streamline literature reviews by automatically labeling and categorizing academic papers using LLM-generated taxonomies.
5. **Customer Insight Generation**: Extract structured insights from customer interactions, enabling deeper understanding for improving product development and strategy.

## 🔨 Usage

1. **Installation**

Install from PyPI:
```
pip install delve-taxonomy-generator
```

Or install from source with the included requirements:
```
git clone https://github.com/andrestorres123/delve.git
cd delve
pip install -r requirements.txt
```

2. **API Keys Setup**
Delve Taxonomy Generator requires an API key for your preferred LLM provider. **OpenAI is the default provider.**

   * `OPENAI_API_KEY`: Required for the default OpenAI models (primary)
   * `ANTHROPIC_API_KEY`: Optional, if using Anthropic models
   * `FIREWORKS_API_KEY`: Optional, if using Fireworks models
   * `GROQ_API_KEY`: Optional, if using Groq models

You can set these using environment variables or a `.env` file:

```
export OPENAI_API_KEY="your-key-here"
```

**Model Selection:** You can configure the models via environment variables:
```
export LLM_MODEL=openai/gpt-5.4-nano          # Main model (default)
export LLM_FAST_MODEL=openai/gpt-5.4-nano      # Fast model for summaries (default)
```

To switch to Anthropic:
```
export ANTHROPIC_API_KEY="your-key-here"
export LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
export LLM_FAST_MODEL=anthropic/claude-3-haiku-20240307
```

3. **Basic Usage — Direct Corpus Input**

You can pass any arbitrary list of text strings directly to the pipeline:

```python
from taxonomy_generator import graph, strings_to_docs

# Convert a list of strings into documents
texts = [
    "User asked about resetting their password...",
    "Customer complained about billing charges...",
    "User wants to know about shipping times...",
    # ... add as many documents as you need
]

result = await graph.ainvoke({
    "documents": strings_to_docs(texts)
})

# Access the taxonomy results
documents = result['documents']
clusters = result["clusters"]
messages = result['messages']
```

You can also pass pre-structured documents as dicts or Doc objects:

```python
from taxonomy_generator import graph, Doc

result = await graph.ainvoke({
    "documents": [
        Doc(id="1", content="User asked about resetting their password..."),
        Doc(id="2", content="Customer complained about billing charges..."),
    ]
})
```

4. **Legacy Usage — LangSmith Retrieval**

If you have conversation traces stored in LangSmith, you can still use the original retrieval mode:

```python
from taxonomy_generator.graph import graph

# Generate taxonomy from LangSmith conversation runs
result = await graph.ainvoke({
    "project_name": "YOUR_PROJECT_NAME",
    "org_id": "YOUR_LANGSMITH_API_KEY",
    "days": 3  # Number of days to analyze
})

# Access the taxonomy results
documents = result['documents']
clusters = result["clusters"]
messages = result['messages']
```

5. **Command-Line Interface**

You can also run the pipeline directly from the command line:

```bash
# From a corpus file (.txt — one document per line, or .json — array of strings/objects)
python main.py --corpus my_corpus.txt

# From a JSON corpus
python main.py --corpus documents.json

# Override the model
python main.py --corpus my_corpus.txt --model groq/llama-3.3-70b-versatile

# Save results to a folder (creates the folder if it doesn't exist)
python main.py --corpus my_corpus.txt --output ./results

# From LangSmith (legacy)
python main.py --project-name MY_PROJECT --org-id MY_API_KEY --days 3
```

When `--output` is specified, three JSON files are saved to the folder with a timestamp:
- `documents_<timestamp>.json` — Labeled documents with id, content, summary, explanation, and category
- `taxonomy_<timestamp>.json` — All taxonomy iterations (last is final)
- `messages_<timestamp>.json` — Formatted result messages

All `.env` variables are automatically loaded via `python-dotenv`.

6. **Output** The system generates three main output properties:

   * **messages**: Contains a friendly message with the taxonomy information pretty-printed in a human-readable format. This is useful for quick inspection and sharing results with non-technical stakeholders.
   
   * **clusters**: An array of array representing all cluster iterations. Each cluster has an `id`, `name`, and `description` that categorizes related content. The last cluster in the array is the final version used for analysis.
   
   * **documents**: The full collection of labeled documents with rich metadata including:
     - `id`: Unique document identifier
     - `content`: The actual document text
     - `category`: The assigned taxonomy category
     - `summary`: A concise summary of the document content
     - `explanation`: Detailed reasoning behind the categorization


## 🙏 Acknowledgements

This project is based on the research paper "Text Mining at Scale with Large Language Models" by Mengting Wan, Tara Safavi, Sujay Kumar Jauhar, and others. We extend our gratitude to the authors for their groundbreaking work on LLM-powered taxonomy generation and classification.

Special thanks to [Will Fu-Hinthorn](https://github.com/hinthornw) for his collaboration and invaluable help in developing this project.