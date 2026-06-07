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
| **LLM Framework** | LangChain | Model invocation, prompt templates, structured outputs |
| **Configuration** | YAML (`config.yaml`) | Centralized settings with `Settings` dataclasses (see [SETTINGS.md](SETTINGS.md)) |
| **Primary LLM** | OpenAI GPT-5.4 nano (default) | Main reasoning model (configurable via `config.yaml` or `LLM_MODEL` env var) |
| **Fast LLM** | OpenAI GPT-5.4 nano (default) | Summarization and lightweight tasks (configurable via `config.yaml` or `LLM_FAST_MODEL` env var) |
| **Data Source** | Direct corpus input | Document ingestion via `.txt` or `.json` corpus files |
| **Output Schema** | Pydantic models | Structured LLM outputs via `with_structured_output()` |
| **Prompts** | Local (`prompts/` package) | System prompts stored as `.md` files, loaded into `ChatPromptTemplate` at import time |
| **Language** | Python ≥ 3.9 | Async/await throughout |

### Design Principles

- **Zero-shot processing** — No pre-training or fine-tuning required; the system works out-of-the-box on new data.
- **Iterative refinement** — Taxonomy is progressively improved by exposing the LLM to different minibatches of data.
- **Separation of concerns** — Each processing step is an independent graph node with well-defined inputs and outputs.
- **Configurability** — All key parameters (model, batch sizes, cluster limits) are exposed via a `Configuration` dataclass.
- **Structured output** — Pydantic models with `with_structured_output()` ensure reliable, validated LLM responses without regex parsing.

### High-Level Data Flow

```
┌──────────────────┐
│  Corpus File     │
│  (.txt or .json) │
│  strings_to_docs │
└────────┬─────────┘
         │
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
│    get_runs      │  Accept direct corpus input and normalize documents
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
| **Data Ingestion** | `get_runs` | Accepts direct corpus input via `--corpus` flag |
| **Preprocessing** | `summarize` (optional), `get_minibatches` | Creates use-case-aware document summaries (can be skipped) and partitions data into batches |
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
    documents                                         │
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

| Field | Type | Default | Description |
|---|---|---|---|
| `documents` | `List[Doc]` | `[]` | Pre-populated documents for direct corpus input |

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
    content: str               # Raw document text
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

#### Pydantic Output Schemas (`schemas.py`)

```python
class SummaryOutput(BaseModel):
    summary: str
    explanation: str

class Cluster(BaseModel):
    id: str
    name: str
    description: str

class TaxonomyOutput(BaseModel):
    clusters: list[Cluster]
    explanation: str

class LabelOutput(BaseModel):
    reasoning: str
    category: str
```

---

## 5. Node Descriptions

### 5.1 `get_runs` — Data Ingestion

**File:** `nodes/runs_retriever.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Normalize pre-populated documents for the pipeline |
| **Input** | `state.documents` (pre-populated `Doc` objects or dicts) |
| **Output** | `all_documents` (full set), `documents` (working set), `status` |

**Behavior:**
1. Checks that `state.documents` is populated (raises `ValueError` if empty).
2. Normalizes them to `Doc` objects via `docs_from_dicts()` (handles dicts, `Doc` objects, and strings).
3. Sets both `all_documents` and `documents` to the same normalized list.

---

### 5.2 `summarize` — Summary Generation

**File:** `nodes/summary_generator.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Generate concise summaries and explanations for each document |
| **Input** | `state.documents` |
| **Output** | Updated `documents` with `summary` and `explanation` fields populated |
| **Model** | Uses `configuration.fast_llm` (default: OpenAI GPT-5.4 nano) |
| **Can be skipped** | Yes — set `summarization.skip: true` in `config.yaml` |

**Behavior:**
1. Uses a **map-reduce** pattern over documents:
   - **Map**: Each document's content is sent to the LLM with the summary generation prompt.
   - **Reduce**: Summaries are merged back into the document objects.
2. The LLM outputs a structured `SummaryOutput` Pydantic object via `with_structured_output()`.
3. Documents are enriched with `id`, `content`, `summary`, and `explanation`.
4. Summaries are **use-case-aware** — the prompt includes `{use_case}` to produce contextual compression rather than generic summarization.

**Prompt:** `SUMMARY_GENERATION_PROMPT` (from `prompts/` package)

**Skipping:** When `skip_summarization` is `true`, the `get_runs` node routes directly to `get_minibatches` via the `should_summarize` conditional edge. Raw document content is used instead of summaries (with a warning logged). The `format_docs()` utility falls back to `doc.content` when `doc.summary` is `None`.

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
| **Model** | Uses `configuration.model` (main reasoning) |

**Behavior:**
1. Formats the first minibatch's documents as JSON summaries.
2. Sends to LLM with the `TAXONOMY_GENERATION_PROMPT`, specifying:
   - Use case (default: user intent classification)
   - Previous user feedback (if any)
   - Constraints: max clusters, name/description lengths
3. The LLM returns a `TaxonomyOutput` Pydantic object via `with_structured_output()`.
4. Returns the initial cluster list (wrapped in a list for the accumulator pattern).

---

### 5.5 `update_taxonomy` — Iterative Taxonomy Refinement

**File:** `nodes/taxonomy_updater.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Refine the taxonomy by exposing it to the next minibatch |
| **Input** | `state.documents`, `state.clusters`, `state.minibatches` |
| **Output** | Updated `clusters`, `status` |
| **Model** | Uses `configuration.model` (main reasoning) |

**Behavior:**
1. Determines which minibatch to use: `which_mb = len(state.clusters) % len(state.minibatches)`.
   - This cycles through minibatches round-robin if there are more revisions than batches.
2. Provides the LLM with:
   - The current taxonomy (from `state.clusters[-1]`) as JSON.
   - The next minibatch of document summaries as JSON.
3. The LLM returns a `TaxonomyOutput` Pydantic object, which is appended to the clusters list via the `operator.add` reducer.

**Prompt:** `TAXONOMY_UPDATE_PROMPT` (from `prompts/` package)

**Looping:** This node loops back to itself via the conditional edge until all minibatches have been processed (see [§6 Routing](#6-routing--control-flow)).

---

### 5.6 `review_taxonomy` — Final Quality Review

**File:** `nodes/taxonomy_reviewer.py`

| Aspect | Detail |
|---|---|
| **Purpose** | Perform a final review and consolidation of the taxonomy |
| **Input** | `state.documents`, `state.clusters` |
| **Output** | Final `clusters`, `status` |
| **Model** | Uses `configuration.model` (main reasoning) |

**Behavior:**
1. Takes a random sample of `configuration.review_sample_size` documents (defaults to `batch_size`).
2. Sends the current taxonomy and sample to the LLM for review (as JSON).
3. The LLM may merge, split, rename, or refine categories.
4. Returns the final taxonomy version as a `TaxonomyOutput` Pydantic object.

**Prompt:** `TAXONOMY_REVIEW_PROMPT` (from `prompts/` package)

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
2. Formats the taxonomy as JSON via `format_taxonomy()`.
3. Processes documents in batches of `configuration.batch_size`.
4. For each document, the LLM:
   - Reads the content and taxonomy.
   - Returns a `LabelOutput` Pydantic object with `reasoning` and `category` fields.
5. Labels are assigned to each `Doc.category`.
6. If no category fits, defaults to `"Other"`.
7. Generates a formatted `AIMessage` with classification results including document previews and labels.

**Prompt:** `LABELER_PROMPT` (from `prompts/` package)

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
| `get_runs` | `summarize` | Conditional | `skip_summarization=false` (default) |
| `get_runs` | `get_minibatches` | Conditional | `skip_summarization=true` |
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

Settings are managed through a layered system: **YAML config file** → **environment variables** → **CLI flags**. See [SETTINGS.md](SETTINGS.md) for the complete reference.

**Files:** `config.yaml`, `settings.py`, `configuration.py`

**Resolution order** (highest priority wins):
1. CLI flags (`--model`, `--fast-model`)
2. Environment variables (`LLM_MODEL`, `LLM_FAST_MODEL`)
3. YAML config file (`config.yaml`)
4. Built-in code defaults (`Settings` dataclass)

#### Models

| Parameter | Type | Default | YAML Key | Description |
|---|---|---|---|---|
| `model` | `str` | `openai/gpt-5.4-nano` | `models.model` | Primary LLM for taxonomy generation, update, and review |
| `fast_llm` | `str` | `openai/gpt-5.4-nano` | `models.fast_llm` | Lighter LLM for summarization and labeling |

#### Pipeline

| Parameter | Type | Default | YAML Key | Description |
|---|---|---|---|---|
| `max_runs` | `int` | `0` (no limit) | `pipeline.max_runs` | Maximum documents to process |
| `sample_size` | `int` | `0` (use all) | `pipeline.sample_size` | Documents to randomly sample |
| `batch_size` | `int` | `200` | `pipeline.batch_size` | Minibatch size for taxonomy iteration |
| `random_seed` | `int` | `42` | `pipeline.random_seed` | Random seed for reproducibility |

#### Taxonomy

| Parameter | Type | Default | YAML Key | Description |
|---|---|---|---|---|
| `use_case` | `str` | User intent classification | `taxonomy.use_case` | Use case description for LLM |
| `max_num_clusters` | `int` | `25` | `taxonomy.max_num_clusters` | Maximum taxonomy categories |
| `cluster_name_length` | `int` | `10` | `taxonomy.cluster_name_length` | Max words for cluster names |
| `cluster_description_length` | `int` | `30` | `taxonomy.cluster_description_length` | Max words for cluster descriptions |
| `suggestion_length` | `int` | `30` | `taxonomy.suggestion_length` | Max words for taxonomy suggestions |
| `explanation_length` | `int` | `20` | `taxonomy.explanation_length` | Max words for explanations |
| `review_sample_size` | `int` | `null` (uses `batch_size`) | `taxonomy.review_sample_size` | Documents sampled for review |

#### Summarization & Labeling

| Parameter | Type | Default | YAML Key | Description |
|---|---|---|---|---|
| `summary_length` | `int` | `20` | `summarization.summary_length` | Max words for document summaries |
| `summary_explanation_length` | `int` | `30` | `summarization.summary_explanation_length` | Max words for summary explanations |
| `fallback_category` | `str` | `"Other"` | `labeling.fallback_category` | Category when no taxonomy match |

### Prompt Templates

#### System prompts are stored as Markdown files in the `prompts/` package

| Prompt Name | Used By | Purpose |
|---|---|---|
| `SUMMARY_GENERATION_PROMPT` | `summarize` | Document summary and explanation generation |
| `TAXONOMY_GENERATION_PROMPT` | `generate_taxonomy` | Initial taxonomy creation from first minibatch |
| `TAXONOMY_UPDATE_PROMPT` | `update_taxonomy` | Iterative taxonomy refinement |
| `TAXONOMY_REVIEW_PROMPT` | `review_taxonomy` | Final taxonomy quality review |
| `LABELER_PROMPT` | `label_documents` | Document classification using the taxonomy |

#### Input Format

All prompts use **JSON** for passing structured data to the LLM:
- Document summaries are formatted as JSON arrays via `format_docs()`
- Taxonomy clusters are formatted as JSON arrays via `format_taxonomy()`

#### Output Format

All LLM outputs use **Pydantic structured outputs** via `with_structured_output()`:

| Output Type | Schema | Fields |
|---|---|---|
| Document summaries | `SummaryOutput` | `summary`, `explanation` |
| Taxonomy clusters | `TaxonomyOutput` | `clusters` (list of `Cluster`), `explanation` |
| Document labels | `LabelOutput` | `reasoning`, `category` |

---

## 8. Utilities & Data Transformation

**File:** `utils.py`

### Core Utilities

| Function | Purpose |
|---|---|
| `strings_to_docs(texts)` | Converts a `List[str]` into `List[Doc]` with auto-generated UUIDs |
| `docs_from_dicts(dicts)` | Normalizes a mixed list of dicts, `Doc` objects, or strings into `List[Doc]` |
| `load_chat_model(name)` | Parses `"provider/model"` string and initializes a LangChain `BaseChatModel` |
| `format_docs(docs)` | Formats documents as JSON for taxonomy prompts |
| `format_taxonomy(clusters)` | Formats clusters as JSON for update/review/labeler prompts |
| `invoke_taxonomy_chain(chain, state, config, indices)` | Orchestrates a taxonomy chain invocation with minibatch data |

### `invoke_taxonomy_chain` — Chain Orchestrator

This is the central helper for all taxonomy-related nodes. It:
1. Selects the minibatch documents by index.
2. Formats documents as JSON via `format_docs()`.
3. Retrieves the previous taxonomy from `state.clusters[-1]`.
4. Formats the previous taxonomy as JSON via `format_taxonomy()`.
5. Formats user feedback if present.
6. Invokes the chain with all context.
7. The chain returns a `TaxonomyOutput` Pydantic object directly.
8. Converts the Pydantic model to dict list and returns the updated clusters appended to the accumulator.

### Data Transformation Pipeline

```
List[str] ──strings_to_docs()──▶ Doc (id=UUID, content=text)
                                        │
                                _get_content()
                                        │
                                        ▼
                                LLM Summary Chain
                                (SummaryOutput via with_structured_output)
                                        │
                                        ▼
                                Doc (summary, explanation)
                                        │
                                format_docs() → JSON
                                        │
                                        ▼
                                Taxonomy Chain
                                (TaxonomyOutput via with_structured_output)
                                        │
                                        ▼
                                Cluster[{id, name, description}]
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
| `pydantic` | ≥ 2.0 | Structured output schemas and validation |
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

### Installation

```bash
pip install delve-taxonomy-generator
```

### Usage — Direct Corpus Input

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

---

## Appendix: File Structure

```
delve/
├── pyproject.toml                          # Package configuration
├── langgraph.json                          # LangGraph deployment config
├── config.yaml                             # YAML configuration file
├── main.py                                 # CLI entry point (argparse-based)
├── .env.example                            # Environment variable template
├── examples/                               # Example corpus files
│   ├── customer_support.txt                #   Text corpus (one doc per line)
│   └── product_reviews.json                #   JSON corpus (array of objects)
├── README.md                               # Project overview and usage
├── DESIGN.md                               # This document
├── SETTINGS.md                             # Complete settings reference
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
        ├── configuration.py                # LangGraph Configuration dataclass
        ├── settings.py                     # YAML settings loader & dataclasses
        ├── graph.py                        # LangGraph StateGraph definition
        ├── schemas.py                      # Pydantic output schemas
        ├── prompts/                        # Prompt templates (system prompts as .md files)
        │   ├── __init__.py                 #   Loads .md files into ChatPromptTemplate
        │   ├── summary_generation.md       #   Summary generation system prompt
        │   ├── taxonomy_generation.md      #   Taxonomy generation system prompt
        │   ├── taxonomy_update.md          #   Taxonomy update system prompt
        │   ├── taxonomy_review.md          #   Taxonomy review system prompt
        │   └── labeler.md                  #   Document labeling system prompt
        ├── state.py                        # State dataclasses (Input/Output/State)
        ├── utils.py                        # Shared utilities and helpers
        ├── nodes/
        │   ├── __init__.py
        │   ├── runs_retriever.py           # Document normalization (direct corpus input)
        │   ├── summary_generator.py        # LLM-powered document summarization
        │   ├── minibatches_generator.py    # Document shuffling and batching
        │   ├── taxonomy_generator.py       # Initial taxonomy creation
        │   ├── taxonomy_updater.py         # Iterative taxonomy refinement
        │   ├── taxonomy_reviewer.py        # Final taxonomy quality review
        │   └── doc_labeler.py             # Document classification
        └── routing/
            ├── __init__.py
            ├── should_review.py            # Taxonomy update loop routing
            └── should_summarize.py         # Summarization skip routing
