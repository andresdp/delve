# Delve — High-Level Design Documentation

> **TnT-LLM: Text Mining at Scale with Large Language Models**
> An implementation of the taxonomy generation pipeline from [Wan et al. (2024)](https://arxiv.org/abs/2403.12173)

---

## Table of Contents

1. [Introduction & Overview](#1-introduction--overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Workflow Pipeline](#3-workflow-pipeline)
4. [State Management](#4-state-management)
5. [Node Descriptions](#5-node-descriptions)
6. [Routing & Control Flow](#6-routing--control-flow)
7. [Configuration & Prompt Engineering](#7-configuration--prompt-engineering)
8. [Utilities & Data Transformation](#8-utilities--data-transformation)
9. [Dependencies & Deployment](#9-dependencies--deployment)

---

## 1. Introduction & Overview

### What is Delve?

Delve is a Python package (`delve-taxonomy-generator`) that implements the **TnT-LLM framework** — a system for large-scale text mining using Large Language Models. It automates two traditionally labor-intensive tasks:

1. **Label Taxonomy Generation** — A zero-shot, multi-stage process where LLMs automatically generate, iteratively refine, and review a label taxonomy from input text data.
2. **Text Classification** — LLMs classify each document using the generated taxonomy, producing labeled output with categories, summaries, and explanations.

### Relationship to the Research Paper

This project is a production-oriented implementation of the approach described in *"Text Mining at Scale with Large Language Models"* (Wan, Safavi, Jauhar et al., 2024). The paper introduces TnT-LLM as a framework that combines the accuracy of LLMs with the scalability of traditional classifiers. This implementation focuses on **Phase A** of the paper — the automated taxonomy generation and zero-shot labeling pipeline — built on top of the [LangGraph](https://github.com/langchain-ai/langgraph) orchestration framework.

### Core Value Proposition

| Challenge | Traditional Approach | Delve (TnT-LLM) |
|---|---|---|
| Taxonomy creation | Manual annotation by domain experts | Zero-shot LLM generation with iterative refinement |
| Text classification | Hand-labeled training data | LLM-generated pseudo-labels |
| Scalability | Limited by human throughput | LLM processing with minibatch iteration |
| Adaptability | Fixed taxonomies | Configurable, feedback-driven taxonomy evolution |

---

## 2. Architecture Overview

### Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Orchestration** | LangGraph (`StateGraph`) | Directed graph execution with conditional routing |
| **LLM Framework** | LangChain | Model invocation, prompt templates, output parsing |
| **Primary LLM** | OpenAI GPT-5.4 nano (default) | Main reasoning model (configurable via `LLM_MODEL` env var) |
| **Fast LLM** | OpenAI GPT-5.4 nano (default) | Summarization and lightweight tasks (configurable via `LLM_FAST_MODEL` env var) |
| **Data Source** | Any (via direct corpus input) or LangSmith (legacy) | Document ingestion via arbitrary text lists or LangSmith run retrieval |
| **Prompts** | Local (`prompts.py`) | All prompt templates defined inline — no external prompt hub |
| **Language** | Python ≥ 3.9 | Async/await throughout |

### Design Principles

- **Zero-shot processing** — No pre-training or fine-tuning required; the system works out-of-the-box on new data.
- **Iterative refinement** — Taxonomy is progressively improved by exposing the LLM to different minibatches of data.
- **Separation of concerns** — Each processing step is an independent graph node with well-defined inputs and outputs.
- **Configurability** — All key parameters (model, batch sizes, cluster limits) are exposed via a `Configuration` dataclass.
- **Structured output** — XML-based prompt engineering ensures reliable parsing of LLM responses.

### High-Level Data Flow

```
┌──────────────────┐    ┌──────────────────┐
│  Arbitrary Text  │    │  LangSmith Runs  │
│  (List[str])     │    │  (Legacy Mode)   │
│  strings_to_docs │    │  run_to_doc      │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
            ┌────────────────┐     ┌──────────────────┐
            │  Document      │────▶│  LLM Summary     │
            │  Normalization │     │  Generation      │
            └────────────────┘     └──────────────────┘
                                          │
                                          ▼
┌──────────────┐     ┌───────────────┐     ┌──────────────────┐
│  Labeled     │◀────│  Taxonomy     │◀────│  Minibatch       │
│  Documents   │     │  Review       │     │  Generation      │
└──────────────┘     └───────────────┘     └──────────────────┘
                             ▲                       │
                             │                       ▼
                     ┌───────────────┐        ┌──────────────┐
                     │  Review       │◀───────│  Taxonomy    │◀──┐
                     │  (final pass) │   done │  Update      │   │
                     └───────────────┘        └──────────────┘   │
                                                           │     │
                                                           └─────┘
                                                             loop
                                                        (per minibatch)
```

---

## 3. Workflow Pipeline

### Graph Definition

The pipeline is defined as a **LangGraph `StateGraph`** with 7 nodes, 7 fixed edges, and 1 conditional edge. The graph is compiled and exposed as an async-invocable `graph` object.

```python
# Entry point: graph.py
builder = StateGraph(State, input=InputState, output=OutputState, config_schema=Configuration)
```

### Node Sequence

```
START
  │
  ▼
┌─────────────────┐
│    get_runs      │  Accept direct corpus or retrieve from LangSmith
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    summarize     │  Generate summaries for each document via LLM
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ get_minibatches  │  Shuffle and partition document indices into batches
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│generate_taxonomy │  Create initial taxonomy from first minibatch
└────────┬────────┘
         │
         ▼
┌─────────────────┐        ┌──────────────────┐
│ update_taxonomy  │───────▶│ update_taxonomy   │  (loop: one iteration per minibatch)
└────────┬────────┘  more  └──────────────────┘
         │          batches
         │ all batches
         │ processed
         ▼
┌─────────────────┐
│ review_taxonomy  │  Final quality review pass on random sample
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ label_documents  │  Classify all documents using the finalized taxonomy
└────────┬────────┘
         │
         ▼
        END
```

### Pipeline Phases

| Phase | Nodes | Description |
|---|---|---|
| **Data Ingestion** | `get_runs` | Accepts direct corpus input or fetches from LangSmith (legacy) |
| **Preprocessing** | `summarize`, `get_minibatches` | Creates document summaries and partitions data into batches |
| **Taxonomy Generation** | `generate_taxonomy` | Produces the initial taxonomy from the first minibatch |
| **Iterative Refinement** | `update_taxonomy` (loop) | Refines taxonomy by exposing it to each subsequent minibatch |
| **Quality Review** | `review_taxonomy` | Final review pass on a random document sample |
| **Classification** | `label_documents` | Assigns categories to all documents using the final taxonomy |

---

## 4. State Management

### Three-Tier State Model

The system uses a layered state architecture via Python dataclasses:

```
InputState ──────────────────────────────────────────┐
   project_name, org_id, days                        │
                                                     ├──▶ State (internal)
OutputState ─────────────────────────────────────────┘       │
   messages, clusters, documents                            │
                                                            │
                                                   + additional fields:
                                                   all_documents, minibatches,
                                                   status, use_case,
                                                   is_last_step, user_feedback
```

### `InputState` — User-Provided Configuration

Supports two input modes: **direct corpus input** (recommended) and **LangSmith retrieval** (legacy).

| Field | Type | Default | Description |
|---|---|---|---|
| `documents` | `List[Doc]` | `[]` | Pre-populated documents for direct corpus input. Skips LangSmith retrieval. |
| `project_name` | `str` | `""` | LangSmith project name to query (legacy mode) |
| `org_id` | `str` | `""` | LangSmith API key (legacy mode) |
| `days` | `int` | `3` | Number of days to look back for runs (legacy mode) |

### `OutputState` — Results Returned to Caller

| Field | Type | Description |
|---|---|---|
| `messages` | `Sequence[AnyMessage]` | Human-readable results with formatted classification output |
| `clusters` | `List[List[Dict]]` | All taxonomy iterations (last is final) |
| `documents` | `List[Doc]` | Fully labeled documents with categories |

### `State` — Complete Internal State

Extends both `InputState` and `OutputState` with:

| Field | Type | Reducer | Description |
|---|---|---|---|
| `all_documents` | `List[Doc]` | replace | Full document set (unsampled) |
| `documents` | `List[Doc]` | replace | Working document set (sampled) |
| `minibatches` | `List[List[int]]` | replace | Document index partitions |
| `clusters` | `List[List[Dict]]` | `operator.add` (append) | Accumulates taxonomy iterations |
| `status` | `List[str]` | `operator.add` (append) | Status messages from each node |
| `use_case` | `str` | replace | Target use case description |
| `is_last_step` | `IsLastStep` | replace | LangGraph managed flag |
| `user_feedback` | `UserFeedback` | replace | Optional feedback for taxonomy revision |

### Key Data Structures

#### `Doc` — Document Record

```python
@dataclass
class Doc:
    id: str                    # Unique identifier
    content: str               # Raw document text (XML from LangSmith run)
    summary: Optional[str]     # LLM-generated summary
    explanation: Optional[str] # LLM-generated explanation
    category: Optional[str]    # Assigned taxonomy category
```

#### `UserFeedback` — Feedback for Taxonomy Revision

```python
class UserFeedback(BaseModel):
    decision: Literal["continue", "modify"]
    explanation: str
    feedback: Optional[str] = None
```

#### Cluster (Taxonomy Category)

```python
# Each cluster is a dictionary:
{
    "id": str,           # Category number (e.g., "1")
    "name": str,         # Short category name
    "description": str   # Category description
}
```

---

## 5. Node Descriptions

### 5.1 `get_runs` — Data Ingestion (Dual Mode)

**File:** `nodes/runs_retriever.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Ingest documents from either a direct corpus or LangSmith |
| **Input (direct mode)** | `state.documents` (pre-populated `Doc` objects or dicts) |
| **Input (LangSmith mode)** | `state.project_name`, `state.org_id`, `state.days` |
| **Output** | `all_documents` (full set), `documents` (working set), `status` |

**Behavior (direct corpus input mode):**
1. Checks if `state.documents` is already populated.
2. If so, normalizes them to `Doc` objects via `docs_from_dicts()` (handles dicts, `Doc` objects, and strings).
3. Sets both `all_documents` and `documents` to the same normalized list (no sampling).
4. Returns immediately without contacting LangSmith.

**Behavior (LangSmith retrieval mode — legacy):**
1. Falls back to LangSmith when `state.documents` is empty and `project_name` is set.
2. Connects to LangSmith using the provided API key.
3. Queries root runs from the specified project, filtered by the lookback window (`days`).
4. Limits results to `configuration.max_runs` (default: 500).
5. Produces two document sets:
   - `all_documents` — the complete retrieved set.
   - `documents` — a random sample of `configuration.sample_size` (default: 50).
6. Each run is converted to a `Doc` via `run_to_doc()`, extracting XML-formatted inputs/outputs.

---

### 5.2 `summarize` — Summary Generation

**File:** `nodes/summary_generator.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Generate concise summaries and explanations for each document |
| **Input** | `state.documents` |
| **Output** | Updated `documents` with `summary` and `explanation` fields populated |
| **Model** | Uses `configuration.fast_llm` (default: OpenAI GPT-5.4 nano) |

**Behavior:**
1. Uses a **map-reduce** pattern over documents:
   - **Map**: Each document's content is sent to the LLM with the summary generation prompt.
   - **Reduce**: Summaries are merged back into the document objects.
2. The LLM outputs structured XML with `<summary>` and `<explanation>` tags.
3. XML is parsed via regex to extract both fields.
4. Documents are enriched with `id`, `content`, `summary`, and `explanation`.

**Prompt:** `SUMMARY_GENERATION_PROMPT` (from `prompts.py`)

---

### 5.3 `get_minibatches` — Batch Partitioning

**File:** `nodes/minibatches_generator.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Shuffle and partition document indices into minibatches for iterative processing |
| **Input** | `state.documents` |
| **Output** | `minibatches` (list of index lists), `status` |

**Behavior:**
1. Creates a list of indices `[0, 1, ..., N-1]` for the sampled documents.
2. Randomly shuffles the indices.
3. Partitions into batches of `configuration.batch_size` (default: 200).
4. If the last batch is smaller than `batch_size`, it is padded with random samples from earlier indices to maintain consistent size.

---

### 5.4 `generate_taxonomy` — Initial Taxonomy Creation

**File:** `nodes/taxonomy_generator.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Generate the initial label taxonomy from the first minibatch |
| **Input** | `state.documents` (via first minibatch), `state.user_feedback` |
| **Output** | `clusters` (initial taxonomy), `status` |
| **Model** | Uses `configuration.fast_llm` |

**Behavior:**
1. Formats the first minibatch's documents as XML summaries.
2. Sends to LLM with the `TAXONOMY_GENERATION_PROMPT`, specifying:
   - Use case (default: user intent classification)
   - Previous user feedback (if any)
   - Constraints: max clusters, name/description lengths
3. Parses the LLM's XML response into structured cluster dictionaries.
4. Returns the initial cluster list (wrapped in a list for the accumulator pattern).

---

### 5.5 `update_taxonomy` — Iterative Taxonomy Refinement

**File:** `nodes/taxonomy_updater.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Refine the taxonomy by exposing it to the next minibatch |
| **Input** | `state.documents`, `state.clusters`, `state.minibatches` |
| **Output** | Updated `clusters`, `status` |
| **Model** | Uses `configuration.fast_llm` |

**Behavior:**
1. Determines which minibatch to use: `which_mb = len(state.clusters) % len(state.minibatches)`.
   - This cycles through minibatches round-robin if there are more revisions than batches.
2. Provides the LLM with:
   - The current taxonomy (from `state.clusters[-1]`).
   - The next minibatch of document summaries.
3. The LLM updates the taxonomy, which is appended to the clusters list via the `operator.add` reducer.

**Prompt:** `TAXONOMY_UPDATE_PROMPT` (from `prompts.py`)

**Looping:** This node loops back to itself via the conditional edge until all minibatches have been processed (see [§6 Routing](#6-routing--control-flow)).

---

### 5.6 `review_taxonomy` — Final Quality Review

**File:** `nodes/taxonomy_reviewer.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Perform a final review and consolidation of the taxonomy |
| **Input** | `state.documents`, `state.clusters` |
| **Output** | Final `clusters`, `status` |
| **Model** | Uses `configuration.fast_llm` |

**Behavior:**
1. Takes a random sample of `configuration.batch_size` documents.
2. Sends the current taxonomy and sample to the LLM for review.
3. The LLM may merge, split, rename, or refine categories.
4. Returns the final taxonomy version.

**Prompt:** `TAXONOMY_REVIEW_PROMPT` (from `prompts.py`)

---

### 5.7 `label_documents` — Document Classification

**File:** `nodes/doc_labeler.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Classify all documents using the finalized taxonomy |
| **Input** | `state.documents`, `state.clusters` |
| **Output** | Labeled `documents`, `messages` (formatted results), `status` |
| **Model** | Uses `configuration.fast_llm` |

**Behavior:**
1. Retrieves the latest complete cluster set from `state.clusters`.
2. Formats the taxonomy as XML (`<cluster_table>`).
3. Processes documents in batches of `configuration.batch_size`.
4. For each document, the LLM:
   - Reads the content and taxonomy.
   - Produces reasoning within `<reasoning>` tags.
   - Outputs the selected category within `<category>` tags.
5. Labels are parsed and assigned to each `Doc.category`.
6. If no category fits, defaults to `"Other"`.
7. Generates a formatted `AIMessage` with classification results including document previews and labels.

**Prompt:** `LABELER_PROMPT` (defined in `prompts.py`)

---

## 6. Routing & Control Flow

### Conditional Edge: `should_review`

**File:** `routing/should_review.py`

The only conditional routing decision in the graph determines whether the taxonomy refinement loop continues or transitions to the review phase.

```python
def should_review(state: State) -> Literal["update_taxonomy", "review_taxonomy"]:
    num_minibatches = len(state.minibatches)
    num_revisions = len(state.clusters)
    if num_revisions < num_minibatches:
        return "update_taxonomy"    # Continue looping
    return "review_taxonomy"        # Exit loop → review
```

**Logic:**
- The number of revisions equals `len(state.clusters)` because each pass through `generate_taxonomy` or `update_taxonomy` appends a new cluster list via the `operator.add` reducer.
- The loop runs until the taxonomy has been refined once per minibatch.
- Once all minibatches are consumed, the flow proceeds to `review_taxonomy`.

### Edge Map

| From | To | Type | Condition |
|---|---|---|---|
| `START` | `get_runs` | Fixed | — |
| `get_runs` | `summarize` | Fixed | — |
| `summarize` | `get_minibatches` | Fixed | — |
| `get_minibatches` | `generate_taxonomy` | Fixed | — |
| `generate_taxonomy` | `update_taxonomy` | Fixed | — |
| `update_taxonomy` | `update_taxonomy` | Conditional | `num_revisions < num_minibatches` |
| `update_taxonomy` | `review_taxonomy` | Conditional | `num_revisions >= num_minibatches` |
| `review_taxonomy` | `label_documents` | Fixed | — |
| `label_documents` | `END` | Fixed | — |

### Iteration Example

Given `sample_size=50` documents and `batch_size=200`:
- One minibatch is created (50 < 200, so the single batch is the full set).
- `generate_taxonomy` produces clusters[0] (1 revision).
- `should_review` checks: 1 revision ≥ 1 minibatch → proceed to `review_taxonomy`.

Given `sample_size=500` documents and `batch_size=200`:
- Three minibatches are created: [200], [200], [200] (last one padded).
- `generate_taxonomy` produces clusters[0] (1 revision).
- `update_taxonomy` → clusters[1] (2 revisions) → loop → clusters[2] (3 revisions).
- `should_review` checks: 3 revisions ≥ 3 minibatches → proceed to `review_taxonomy`.

---

## 7. Configuration & Prompt Engineering

### Configuration Parameters

**File:** `configuration.py`

All parameters are configurable via the LangGraph `RunnableConfig` mechanism.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `str` | `"openai/gpt-5.4-nano"` (via `LLM_MODEL` env var) | Primary LLM for main reasoning tasks |
| `fast_llm` | `str` | `"openai/gpt-5.4-nano"` (via `LLM_FAST_MODEL` env var) | Lighter LLM for summarization and classification |
| `max_runs` | `int` | `500` | Maximum number of runs to retrieve from LangSmith (legacy only) |
| `sample_size` | `int` | `50` | Number of runs to sample for processing (legacy only) |
| `batch_size` | `int` | `200` | Size of minibatches for taxonomy iteration |
| `suggestion_length` | `int` | `30` | Max words for taxonomy suggestions |
| `cluster_name_length` | `int` | `10` | Max words for cluster names |
| `cluster_description_length` | `int` | `30` | Max words for cluster descriptions |
| `explanation_length` | `int` | `20` | Max words for explanations |
| `max_num_clusters` | `int` | `25` | Maximum number of taxonomy categories |

### Prompt Templates

#### `TAXONOMY_GENERATION_PROMPT` (inline, `prompts.py`)

A structured system/human prompt pair for generating taxonomies from document summaries:

- **System prompt** specifies:
  - Goal: cluster input data into meaningful categories.
  - Input format: XML conversation summaries with `id` and `text`.
  - Use case and previous feedback integration.
  - Output format: XML `<clusters>` with `<id>`, `<name>`, `<description>`.
  - Quality constraints: no overlap, orthogonal coverage, unambiguous labels.

- **Human prompt** requests:
  - Q1: Generate a flat list of mutually exclusive categories.
  - Q2: Explain reasoning within word limits.
  - Output between `<cluster_table>` and `<explanation>` tags.

#### `LABELER_PROMPT` (inline, `prompts.py`)

A system/human prompt pair for document classification:

- **System prompt**: Provides the taxonomy and instructs the LLM to:
  - Read the content, identify the single most relevant category.
  - Output reasoning in `<reasoning>` tags.
  - Output category in `<category>` tags.
  - Default to "Other" if no category fits.

- **Human prompt**: Provides the content to classify in `<content>` tags.

#### All prompts are defined locally in `prompts.py`

| Prompt Name | Used By | Purpose |
|---|---|---|
| `SUMMARY_GENERATION_PROMPT` | `summarize` | Document summary and explanation generation |
| `TAXONOMY_GENERATION_PROMPT` | `generate_taxonomy` | Initial taxonomy creation from first minibatch |
| `TAXONOMY_UPDATE_PROMPT` | `update_taxonomy` | Iterative taxonomy refinement |
| `TAXONOMY_REVIEW_PROMPT` | `review_taxonomy` | Final taxonomy quality review |
| `LABELER_PROMPT` | `label_documents` | Document classification using the taxonomy |

### Structured Output Parsing

All LLM outputs use **XML-based structured formatting** parsed via regex:

| Output Type | Parser | Pattern |
|---|---|---|
| Taxonomy clusters | `parse_taxa()` | `<id>...</id><name>...</name><description>...</description>` |
| Document summaries | `_parse_summary()` | `<summary>...</summary>` and `<explanation>...</explanation>` |
| Document labels | `_parse_labels()` | `<category>...</category>` |

---

## 8. Utilities & Data Transformation

**File:** `utils.py`

### Core Utilities

| Function | Purpose |
|---|---|
| `strings_to_docs(texts)` | Converts a `List[str]` into `List[Doc]` with auto-generated UUIDs |
| `docs_from_dicts(dicts)` | Normalizes a mixed list of dicts, `Doc` objects, or strings into `List[Doc]` |
| `load_chat_model(name)` | Parses `"provider/model"` string and initializes a LangChain `BaseChatModel` |
| `to_xml(data, tag, ...)` | Generic recursive dict/list → XML converter with include/exclude/filtering options |
| `run_to_doc(run)` | Converts a LangSmith `Run` object into a `Doc` with XML-formatted content (legacy) |
| `process_runs(left, right, sample)` | Merges document lists with optional random sampling (legacy) |
| `parse_taxa(text)` | Extracts cluster definitions from LLM XML output |
| `format_docs(docs)` | Formats documents as `<conv_summ>` XML for taxonomy prompts |
| `format_taxonomy(clusters)` | Formats clusters as `<cluster_table>` XML for update/review prompts |
| `invoke_taxonomy_chain(chain, state, config, indices)` | Orchestrates a taxonomy chain invocation with minibatch data |

### `invoke_taxonomy_chain` — Chain Orchestrator

This is the central helper for all taxonomy-related nodes. It:
1. Selects the minibatch documents by index.
2. Formats documents as XML via `format_docs()`.
3. Retrieves the previous taxonomy from `state.clusters[-1]`.
4. Formats the previous taxonomy as XML via `format_taxonomy()`.
5. Formats user feedback if present.
6. Invokes the chain with all context.
7. Returns the updated clusters appended to the accumulator.

### Data Transformation Pipeline

**Direct corpus input mode (recommended):**

```
List[str] ──strings_to_docs()──▶ Doc (id=UUID, content=text)
                                        │
                                _get_content()
                                        │
                                        ▼
                                LLM Summary Chain
                                        │
                                _parse_summary()
                                        │
                                        ▼
                                Doc (summary, explanation)
                                        │
                                format_docs()
                                        │
                                        ▼
                                XML <conversations> ──▶ Taxonomy Chain
                                                                │
                                                        parse_taxa()
                                                                │
                                                                ▼
                                                Cluster[{id, name, description}]
```

**LangSmith retrieval mode (legacy):**

```
LangSmith Run ──run_to_doc()──▶ Doc (content=XML)
                                       │
                               (same pipeline as above)
```

---

## 9. Dependencies & Deployment

### Package Dependencies

| Package | Version | Purpose |
|---|---|---|
| `langgraph` | ≥ 0.2.6 | Graph-based workflow orchestration |
| `langchain` | ≥ 0.2.14 | LLM abstraction layer |
| `langchain-anthropic` | ≥ 0.1.23 | Anthropic Claude model integration |
| `langchain-openai` | ≥ 0.1.22 | OpenAI model integration |
| `langchain-fireworks` | ≥ 0.1.7 | Fireworks model integration (optional) |
| `langchain-groq` | ≥ 0.1.9 | Groq model integration (optional) |
| `langchain-community` | ≥ 0.2.17 | Community integrations |
| `langchain-ollama` | ≥ 0.1.0 | Ollama local model integration |
| `python-dotenv` | ≥ 1.0.1 | Environment variable management |
| `rich` | ≥ 13.0.0 | Terminal output formatting (tables, panels, styled text) |

### LangGraph Deployment

**File:** `langgraph.json`

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/taxonomy_generator/graph.py:graph"
  },
  "env": ".env"
}
```

This configuration enables deployment to **LangGraph Cloud** or **LangGraph Studio** for interactive development and monitoring.

### Environment Setup

Required environment variable (for default OpenAI models):

```
OPENAI_API_KEY=<your-key>
```

Optional model configuration (via `.env` file or environment variables):

```
LLM_MODEL=openai/gpt-5.4-nano          # Main reasoning model
LLM_FAST_MODEL=openai/gpt-5.4-nano     # Fast model for summaries/labeling
```

Optional (for alternative providers):

```
ANTHROPIC_API_KEY=<your-key>            # For Anthropic models
FIREWORKS_API_KEY=<your-key>            # For Fireworks models
GROQ_API_KEY=<your-key>                 # For Groq models
```

Using Ollama (local models, no API key needed):

```
# Ensure Ollama is running locally (ollama serve)
LLM_MODEL=ollama/llama3.2
LLM_FAST_MODEL=ollama/llama3.2
```

Optional (for LangSmith tracing / legacy retrieval):

```
LANGSMITH_API_KEY=<your-key>
```

### Installation

```bash
pip install delve-taxonomy-generator
```

### Usage — Direct Corpus Input (Recommended)

```python
from taxonomy_generator import graph, strings_to_docs

# Pass any arbitrary list of text strings
texts = [
    "User asked about resetting their password...",
    "Customer complained about billing charges...",
    "User wants to know about shipping times...",
]

result = await graph.ainvoke({
    "documents": strings_to_docs(texts)
})

# Access results
documents = result['documents']      # Labeled documents
clusters = result["clusters"]        # Taxonomy iterations
messages = result['messages']        # Formatted results
```

### Usage — LangSmith Retrieval (Legacy)

```python
from taxonomy_generator.graph import graph

result = await graph.ainvoke({
    "project_name": "YOUR_PROJECT_NAME",
    "org_id": "YOUR_LANGSMITH_API_KEY",
    "days": 3
})

# Access results
documents = result['documents']      # Labeled documents
clusters = result["clusters"]        # Taxonomy iterations
messages = result['messages']        # Formatted results
```

---

## Appendix: File Structure

```
delve/
├── pyproject.toml                          # Package configuration
├── langgraph.json                          # LangGraph deployment config
├── main.py                                 # CLI entry point (argparse-based)
├── .env.example                            # Environment variable template
├── examples/                               # Example corpus files
│   ├── customer_support.txt                #   Text corpus (one doc per line)
│   └── product_reviews.json                #   JSON corpus (array of objects)
├── README.md                               # Project overview and usage
├── DESIGN.md                               # This document
├── Makefile                                # Build automation
├── LICENSE                                 # MIT License
├── images/
│   └── tnt_llm.png                         # Architecture diagram
├── output/                                 # Generated output (gitignored)
├── paper/
│   └── TNT-LLM-2403.12173v1.pdf           # Original research paper
└── src/
    └── taxonomy_generator/
        ├── __init__.py                     # Package initialization
        ├── configuration.py                # Configuration dataclass
        ├── graph.py                        # LangGraph StateGraph definition
        ├── prompts.py                      # Inline prompt templates
        ├── state.py                        # State dataclasses (Input/Output/State)
        ├── utils.py                        # Shared utilities and helpers
        ├── nodes/
        │   ├── __init__.py
        │   ├── runs_retriever.py           # Data ingestion from LangSmith
        │   ├── summary_generator.py        # LLM-powered document summarization
        │   ├── minibatches_generator.py    # Document shuffling and batching
        │   ├── taxonomy_generator.py       # Initial taxonomy creation
        │   ├── taxonomy_updater.py         # Iterative taxonomy refinement
        │   ├── taxonomy_reviewer.py        # Final taxonomy quality review
        │   └── doc_labeler.py             # Document classification
        └── routing/
            ├── __init__.py
            └── should_review.py            # Conditional routing logic