# Delve — Complete Settings & Configuration Reference

> A comprehensive inventory of every configurable parameter, environment variable, CLI argument, and hardcoded value in the Delve taxonomy generator pipeline.

---

## Table of Contents

1. [Overview](#1-overview)
2. [YAML Configuration File (`config.yaml`)](#2-yaml-configuration-file-configyaml)
3. [Environment Variables](#3-environment-variables)
4. [CLI Arguments](#4-cli-arguments)
5. [Hardcoded Values](#5-hardcoded-values)
6. [Configuration Resolution Order](#6-configuration-resolution-order)
7. [Quick Reference: All Settings](#7-quick-reference-all-settings)

---

## 1. Overview

Settings in Delve are organized in a layered configuration system:

| Layer | Mechanism | Editable at runtime? | Source file(s) |
|---|---|---|---|
| **1. YAML config** | `config.yaml` file | ✅ Yes (before launch) | `config.yaml`, `settings.py` |
| **2. Environment** | OS env vars / `.env` file | ✅ Yes (before launch) | `.env` |
| **3. CLI** | `argparse` command-line flags | ✅ Yes (at invocation) | `main.py` |
| **4. Code defaults** | `Settings` dataclass defaults | ❌ No (requires code change) | `settings.py`, `configuration.py` |
| **5. Hardcoded** | Literal values in source | ❌ No (requires code change) | Various nodes and utils |

The primary configuration mechanism is the **YAML config file** (`config.yaml`), which groups all settings into logical sections. Environment variables and CLI flags act as overrides.

---

## 2. YAML Configuration File (`config.yaml`)

**File:** `config.yaml` (project root)  
**Loader:** `src/taxonomy_generator/settings.py`  
**Consumer:** `src/taxonomy_generator/configuration.py`

All settings are defined in `config.yaml` and loaded via `init_settings()`. The `Configuration` dataclass (used by LangGraph nodes) reads from the resolved `Settings` singleton.

### 2.1 Models

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `models.model` | `str` | `"openai/gpt-5.4-nano"` | Primary LLM for **taxonomy generation, update, and review** (main reasoning tasks). Override via `LLM_MODEL` env var or `--model` CLI flag. |
| `models.fast_llm` | `str` | `"openai/gpt-5.4-nano"` | Lighter LLM for **document summarization and labeling**. Override via `LLM_FAST_MODEL` env var or `--fast-model` CLI flag. |

**Model name format:** `provider/model-name` (e.g., `openai/gpt-4o-mini`, `anthropic/claude-3-haiku-20240307`, `ollama/llama3.2`).

**Supported providers:** `openai`, `anthropic`, `fireworks`, `groq`, `ollama` (and any provider supported by LangChain's `init_chat_model`).

**Which model is used where:**

| Node | Model used | Why |
|---|---|---|
| `summarize` | `fast_llm` | Lightweight summarization task |
| `generate_taxonomy` | `model` | Core reasoning — taxonomy creation |
| `update_taxonomy` | `model` | Core reasoning — taxonomy refinement |
| `review_taxonomy` | `model` | Core reasoning — quality review |
| `label_documents` | `fast_llm` | Repetitive classification task |

### 2.2 Pipeline

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `pipeline.max_runs` | `int` | `500` | Maximum number of documents to process. Caps the corpus to this size. `0` = no limit. |
| `pipeline.sample_size` | `int` | `50` | Number of documents to randomly sample after capping. `0` = use all (after max_runs cap). |
| `pipeline.batch_size` | `int` | `200` | Size of minibatches for iterative taxonomy processing. Also used as default for document labeling batches. |
| `pipeline.random_seed` | `int` or `null` | `42` | Random seed for reproducibility. Affects minibatch shuffling, document sampling, and review sampling. `null` = non-deterministic. |

### 2.3 Taxonomy

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `taxonomy.name` | `str` | `"taxonomy"` | Optional name to identify this taxonomy. Shown in CLI output and included in all generated JSON files. Override via `--name` CLI flag. |
| `taxonomy.use_case` | `str` | `"Generate the taxonomy that can be used to label the user intent in the conversation."` | The use case description sent to the LLM for taxonomy generation and refinement. |
| `taxonomy.max_num_clusters` | `int` | `25` | Maximum number of taxonomy categories the LLM may produce. |
| `taxonomy.cluster_name_length` | `int` | `10` | Max words for cluster/category names. |
| `taxonomy.cluster_description_length` | `int` | `30` | Max words for cluster/category descriptions. |
| `taxonomy.suggestion_length` | `int` | `30` | Max words for taxonomy suggestions. |
| `taxonomy.explanation_length` | `int` | `20` | Max words for taxonomy reasoning explanations. |
| `taxonomy.review_sample_size` | `int` or `null` | `null` | Number of documents to sample for the final taxonomy review. `null` = use `batch_size`. |

### 2.4 Summarization

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `summarization.skip` | `bool` | `false` | Skip the summarization step entirely. When `true`, raw document content is used for taxonomy generation instead of LLM-generated summaries. A warning is logged when enabled. |
| `summarization.summary_length` | `int` | `20` | Max words for document summaries. |
| `summarization.summary_explanation_length` | `int` | `30` | Max words for document summary explanations. |
| `summarization.max_concurrency` | `int` | `5` | Max concurrent LLM requests during summarization. Acts as a semaphore to prevent API rate limit errors. |

### 2.5 Labeling

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `labeling.fallback_category` | `str` | `"Other"` | Category assigned when no taxonomy category fits a document. |

### 2.6 Output

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `output.default_output_dir` | `str` | `"output"` | Default directory for output files (graph PNG, etc.). |
| `output.graph_filename` | `str` | `"graph.png"` | Filename for the auto-exported Mermaid pipeline diagram. |
| `output.max_displayed_documents` | `int` | `20` | Max documents shown in the rich table display. |
| `output.max_docs_per_category_tree` | `int` | `5` | Max documents shown per category in the taxonomy tree view. |
| `output.content_preview_length` | `int` | `100` | Character length for content previews in the display table. |

### Example `config.yaml`

```yaml
models:
  model: openai/gpt-5.4-nano
  fast_llm: openai/gpt-5.4-nano

pipeline:
  max_runs: 500
  sample_size: 50
  batch_size: 200
  random_seed: 42

taxonomy:
  use_case: "Generate the taxonomy that can be used to label the user intent in the conversation."
  max_num_clusters: 25
  cluster_name_length: 10
  cluster_description_length: 30
  suggestion_length: 30
  explanation_length: 20
  review_sample_size: null

summarization:
  skip: false
  summary_length: 20
  summary_explanation_length: 30
  max_concurrency: 5

labeling:
  fallback_category: "Other"

output:
  default_output_dir: "output"
  graph_filename: "graph.png"
  max_displayed_documents: 20
  content_preview_length: 100
```

---

## 3. Environment Variables

**File:** `.env` (loaded via `python-dotenv` in `main.py`)

### 3.1 Model Overrides

| Variable | Default | Description |
|---|---|---|
| `LLM_MODEL` | `openai/gpt-5.4-nano` | Override `models.model` from `config.yaml`. |
| `LLM_FAST_MODEL` | `openai/gpt-5.4-nano` | Override `models.fast_llm` from `config.yaml`. |

### 3.2 API Keys

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes (for OpenAI models) | OpenAI API key. Required when using default models. |
| `ANTHROPIC_API_KEY` | No | Required for Anthropic Claude models. |
| `FIREWORKS_API_KEY` | No | Required for Fireworks models. |
| `GROQ_API_KEY` | No | Required for Groq models. |

### 3.3 Local Models (Ollama)

No API key needed. Ensure Ollama is running locally (`ollama serve`), then configure in `config.yaml`:

```yaml
models:
  model: ollama/llama3.2
  fast_llm: ollama/llama3.2
```

---

## 4. CLI Arguments

**File:** `main.py`

### 4.1 Input Source

| Argument | Type | Default | Required | Description |
|---|---|---|---|---|
| `--corpus` | `str` | — | **Yes** | Path to a corpus file. Supports `.txt` (one document per line, blank lines skipped) or `.json` (JSON array of strings or objects with a `content` field). |

### 4.2 Configuration

| Argument | Type | Default | Description |
|---|---|---|---|
| `--config` | `str` | `None` (uses `./config.yaml`) | Path to a YAML configuration file. If not provided, defaults to `./config.yaml` in the project root. |

### 4.3 Taxonomy

| Argument | Type | Default | Description |
|---|---|---|---|
| `--name` | `str` | `None` | Override the taxonomy name (`taxonomy.name`). Shown in CLI output and included in JSON files. |

### 4.4 Model Overrides

| Argument | Type | Default | Description |
|---|---|---|---|
| `--model` | `str` | `None` | Override the main LLM model (`models.model`). Format: `provider/model-name`. |
| `--fast-model` | `str` | `None` | Override the fast LLM model (`models.fast_llm`). Format: `provider/model-name`. |

### 4.5 Output

| Argument | Type | Default | Description |
|---|---|---|---|
| `--output` | `str` | `None` | Path to a folder where results are saved as timestamped JSON files (`documents_*.json`, `taxonomy_*.json`, `messages_*.json`). Folder is created if it doesn't exist. |
| `--quiet` | flag | `False` | Suppress log output (sets logging to `WARNING`). Shows only rich-formatted tables and panels. Also suppresses graph PNG export. |

---

## 5. Hardcoded Values

These values are embedded directly in the source code and **cannot be changed without editing the files**.

### 5.1 Routing Logic (`routing/should_review.py`)

| Setting | Value | Description |
|---|---|---|
| Loop termination | `num_revisions < num_minibatches` | The update loop runs exactly once per minibatch. Not configurable. |
| Minibatch cycling | `len(state.clusters) % len(state.minibatches)` | If there are more revisions than minibatches, cycles round-robin. |

### 5.2 Logging (`main.py`)

| Setting | Value | Description |
|---|---|---|
| Log format | `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"` | Standard log format. |
| Date format | `"%Y-%m-%d %H:%M:%S"` | Timestamp format for log entries. |
| `httpx` logger level | `logging.WARNING` | Always suppressed, regardless of `--quiet`. |

### 5.3 JSON Formatting (`utils.py`)

| Setting | Value | Description |
|---|---|---|
| JSON indent | `2` spaces | Indentation for JSON sent to the LLM. |
| Document fields in taxonomy prompts | `id`, `summary` | Only these fields are included — `content`, `explanation`, and `category` are stripped. |
| Taxonomy fields in prompts | `id`, `name`, `description` | Only these three fields are included. |
| Default feedback message | `"No previous feedback provided."` | Used when `state.user_feedback` is `None`. |

### 5.4 Prompts (`prompts.py`)

| Setting | Value | Description |
|---|---|---|
| Output language | English | `"Output in **English** only."` in three taxonomy prompts. |
| Cluster ID format | Starting from 1, incremented | Numeric IDs only. |
| Cluster name style | Verb phrase or noun phrase | Specified in prompt instructions. |
| Vague category prohibition | No "Other", "General", etc. | Explicitly prohibited in generation and review prompts. |

### 5.5 Output Files (`main.py`)

| Setting | Value | Description |
|---|---|---|
| Output filename pattern | `{type}_{YYYYMMDD_HHMMSS}.json` | Timestamped JSON files for documents, taxonomy, and messages. |

### 5.6 State Defaults (`state.py`)

| Field | Type | Default | Notes |
|---|---|---|---|
| `user_feedback` | `UserFeedback` | `None` | Supports `"continue"` or `"modify"` decisions. No CLI mechanism to provide feedback. |
| `is_last_step` | `IsLastStep` | `False` | Managed by LangGraph; not user-facing. |

---

## 6. Configuration Resolution Order

Settings are resolved in the following priority order (highest wins):

```
CLI flags (--model, --fast-model)
    ↓ overrides
Environment variables (LLM_MODEL, LLM_FAST_MODEL)
    ↓ overrides
YAML config file (config.yaml)
    ↓ overrides
Code defaults (Settings dataclass defaults)
```

For model settings:
1. `--model` / `--fast-model` CLI flags → highest priority
2. `LLM_MODEL` / `LLM_FAST_MODEL` environment variables
3. `models.model` / `models.fast_llm` in `config.yaml`
4. `"openai/gpt-5.4-nano"` (code default)

For all other settings:
1. `config.yaml` values
2. Code defaults from `Settings` dataclass

---

## 7. Quick Reference: All Settings

### ✅ Configurable via `config.yaml`

| Section | Setting | YAML Key | Default |
|---|---|---|---|
| **Models** | Main reasoning model | `models.model` | `openai/gpt-5.4-nano` |
| **Models** | Fast/lightweight model | `models.fast_llm` | `openai/gpt-5.4-nano` |
| **Pipeline** | Max documents to process | `pipeline.max_runs` | `500` |
| **Pipeline** | Documents to sample | `pipeline.sample_size` | `50` |
| **Pipeline** | Minibatch size | `pipeline.batch_size` | `200` |
| **Pipeline** | Random seed | `pipeline.random_seed` | `42` |
| **Taxonomy** | Taxonomy name | `taxonomy.name` | `"taxonomy"` |
| **Taxonomy** | Use case description | `taxonomy.use_case` | User intent classification |
| **Taxonomy** | Max categories | `taxonomy.max_num_clusters` | `25` |
| **Taxonomy** | Max name length (words) | `taxonomy.cluster_name_length` | `10` |
| **Taxonomy** | Max description length (words) | `taxonomy.cluster_description_length` | `30` |
| **Taxonomy** | Max suggestion length (words) | `taxonomy.suggestion_length` | `30` |
| **Taxonomy** | Max explanation length (words) | `taxonomy.explanation_length` | `20` |
| **Taxonomy** | Review sample size | `taxonomy.review_sample_size` | `null` (uses `batch_size`) |
| **Summarization** | Skip summarization | `summarization.skip` | `false` |
| **Summarization** | Summary length (words) | `summarization.summary_length` | `20` |
| **Summarization** | Summary explanation length (words) | `summarization.summary_explanation_length` | `30` |
| **Summarization** | Max concurrent summarization requests | `summarization.max_concurrency` | `5` |
| **Labeling** | Fallback category | `labeling.fallback_category` | `"Other"` |
| **Output** | Default output directory | `output.default_output_dir` | `"output"` |
| **Output** | Graph PNG filename | `output.graph_filename` | `"graph.png"` |
| **Output** | Max displayed documents | `output.max_displayed_documents` | `20` |
| **Output** | Max docs per category in tree | `output.max_docs_per_category_tree` | `5` |
| **Output** | Content preview length (chars) | `output.content_preview_length` | `100` |

### ✅ Configurable via CLI / Env

| Setting | CLI Flag | Env Var | Config YAML Key |
|---|---|---|---|
| Taxonomy name | `--name` | — | `taxonomy.name` |
| Main model | `--model` | `LLM_MODEL` | `models.model` |
| Fast model | `--fast-model` | `LLM_FAST_MODEL` | `models.fast_llm` |
| Config file path | `--config` | — | — |
| Corpus file | `--corpus` | — | — |
| Output folder | `--output` | — | — |
| Quiet mode | `--quiet` | — | — |

### ❌ Hardcoded (Not Configurable)

| Aspect | Value | File |
|---|---|---|
| Output language | English | `prompts/` package |
| Cluster ID format | Numeric, starting from 1 | `prompts/` package |
| JSON indent for LLM | 2 spaces | `utils.py` |
| Output filename pattern | `{type}_{YYYYMMDD_HHMMSS}.json` | `main.py` |
| Log format | Standard with timestamps | `main.py` |
| Loop termination | One revision per minibatch | `should_review.py` |
| Default feedback message | `"No previous feedback provided."` | `utils.py` |

---

*This document reflects the state of the codebase after the settings centralization refactor. All previously hardcoded values (summary length, use case, fallback category, random seed, etc.) are now configurable via `config.yaml`.*