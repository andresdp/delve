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
| `models.fast_llm` | `str` | `"openai/gpt-5.4-nano"` | Lighter LLM for **document summarization, labeling, open coding, and saturation checks**. Override via `LLM_FAST_MODEL` env var or `--fast-model` CLI flag. |
| `models.embedding` | `str` | `"openai/text-embedding-3-small"` | Embedding model for **value consolidation** and taxonomy **biplot axis positions**. Format: `provider/model-name`. Supported providers: `openai`, `ollama`. |

**Model name format:** `provider/model-name` (e.g., `openai/gpt-4o-mini`, `anthropic/claude-3-haiku-20240307`, `ollama/llama3.2`).

**Supported providers:** `openai`, `anthropic`, `fireworks`, `groq`, `ollama` (and any provider supported by LangChain's `init_chat_model`).

**Which model is used where:**

| Node | Model used | Why |
|---|---|---|
| `summarize` | `fast_llm` | Lightweight summarization task |
| `open_code_minibatch` | `fast_llm` | Repetitive per-document concept extraction |
| `generate_taxonomy` | `model` | Core reasoning — taxonomy creation (axial coding) |
| `update_taxonomy` | `model` | Core reasoning — taxonomy refinement (axial coding) |
| `check_saturation` | `fast_llm` | Lightweight coverage verdict |
| `review_taxonomy` | `model` | Core reasoning — quality review |
| `consolidate_values` | `model` (LLM adjudication only) | Embeddings do the merging; the LLM only adjudicates borderline pairs |
| `select_dimensions` | `model` | Core reasoning — use-case relevance filtering |
| `aggregate_new_values` | `model` | Test mode only — merges labeling-proposed new values into the frozen dimensions |
| `label_documents` | `fast_llm` | Repetitive classification task |

### 2.2 Pipeline

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `pipeline.max_runs` | `int` | `500` | Maximum number of documents to process. Caps the corpus to this size. `0` = no limit. |
| `pipeline.sample_size` | `int` | `50` | Number of documents to randomly sample after capping. `0` = use all (after max_runs cap). |
| `pipeline.batch_size` | `int` | `200` | Size of minibatches for iterative taxonomy processing. Also used as default for document labeling batches. |
| `pipeline.random_seed` | `int` or `null` | `42` | Random seed for reproducibility. Affects minibatch shuffling, document sampling, and review sampling. `null` = non-deterministic. |
| `pipeline.mode` | `str` | `"train"` | Run mode. `"train"` (default) progressively builds and updates the taxonomy. `"test"` freezes the seeded taxonomy's dimensions and only labels new documents against them (new values may be appended via `aggregate_new_values`; no-fit documents go to `labeling.fallback_category`). Override via `--mode` CLI flag. |
| `pipeline.taxonomy_input` | `str` or `null` | `null` | Path to a saved taxonomy JSON (e.g. `output/taxonomy_<timestamp>.json`) used as the run's starting taxonomy. **Required for `--mode test`**; in train mode it seeds refinement instead of generating from scratch. `null` = generate from scratch (current behavior). Override via `--taxonomy` CLI flag. |

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
| `taxonomy.saturation_streak_threshold` | `int` | `2` | Consecutive saturated minibatches required to stop the update loop early (theoretical saturation). Empirically tunable. |
| `taxonomy.value_merge_distance_threshold` | `float` | `0.2` | Embedding-distance cutoff (`epsilon`, Euclidean on L2-normalized vectors) below which two values within the same dimension are merged automatically. Calibrated for `text-embedding-3-small`. |
| `taxonomy.value_merge_borderline_band` | `float` | `0.08` | Distance band above `epsilon` routed to LLM adjudication instead of auto-merge or auto-reject. |
| `taxonomy.consolidate_values` | `bool` | `true` | When `false`, value consolidation is disabled: the `consolidate_values` node passes the reviewed taxonomy through unchanged (no embeddings, no LLM adjudication), and visualization places every value at a unitary distance on its dimension axis. |
| `taxonomy.review_sample_size` | `int` or `null` | `null` | Number of documents to sample for the final taxonomy review. `null` = use `batch_size`. |

### 2.4 Feedback

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `feedback.text` | `str` or `null` | `null` | Inline feedback text injected into taxonomy refinement prompts (update/review). Wins over `feedback.file` when both are set. Override via `--feedback` CLI flag. |
| `feedback.file` | `str` or `null` | `null` | Path to a text/markdown file with feedback for taxonomy refinement. Used only when `feedback.text` is absent. Override via `--feedback-file` CLI flag. |

> **Feedback resolution order:** `--feedback` > `--feedback-file` > `feedback.text` > `feedback.file` > none. The resolved text is wrapped in a `UserFeedback` object and passed to the graph via the input state, flowing into the existing `{feedback}` prompt slot of update and review nodes.

### 2.5 Summarization

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `summarization.skip` | `bool` | `false` | Skip the summarization step entirely. When `true`, raw document content is used for taxonomy generation instead of LLM-generated summaries. A warning is logged when enabled. |
| `summarization.summary_length` | `int` | `20` | Max words for document summaries. |
| `summarization.summary_explanation_length` | `int` | `30` | Max words for document summary explanations. |
| `summarization.max_concurrency` | `int` | `5` | Max concurrent LLM requests during summarization. Acts as a semaphore to prevent API rate limit errors. |

### 2.6 Labeling

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `labeling.fallback_category` | `str` | `"Other"` | Category assigned when no taxonomy category fits a document. |

### 2.7 Output

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `output.default_output_dir` | `str` | `"output"` | Default directory for output files (graph PNG, etc.). |
| `output.graph_filename` | `str` | `"graph.png"` | Filename for the auto-exported Mermaid pipeline diagram. |
| `output.max_displayed_documents` | `int` | `20` | Max documents shown in the rich table display. |
| `output.max_docs_per_category_tree` | `int` | `5` | Max documents shown per category in the taxonomy tree view. |
| `output.content_preview_length` | `int` | `100` | Character length for content previews in the display table. |

### 2.8 Visualization

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `visualization.enabled` | `bool` | `false` | Master on/off switch for taxonomy biplot chart export. Off by default so normal runs pay no extra cost/latency. |
| `visualization.every_iteration` | `bool` | `false` | If `false`, only render the final (post-consolidation) chart; if `true`, render at every stage (generate/update/review/consolidate). |
| `visualization.dimensions` | `int` | `2` | Chart size: `2` or `3`. Taxonomies with no more dimensions than this render exactly (no PCA); taxonomies with more (including exactly 3 dimensions when this is `2`) are PCA-reduced to this many components. |
| `visualization.output_dir` | `str` or `null` | `null` | Directory for chart files (`taxonomy_biplot_<name>_<stage>_<iter>.html`). `null` = use `output.default_output_dir` / `--output`. |

> **Biplot semantics:** the design matrix has one row per *value* and one column per *dimension*. A value's entry in its own dimension's column encodes its position along that axis — derived from the same embedding geometry used by consolidation (reduced to 1-D via classical MDS within each dimension) when `taxonomy.consolidate_values` is `true`, or a unitary `1.0` otherwise. When a taxonomy has more dimensions than `visualization.dimensions`, the matrix is PCA-reduced to that many components; each dimension's loading direction is drawn as a full, equal-radius axis through the origin (not a one-way arrow scaled to its own magnitude), and each value's point sits on its own dimension's axis at a distance reflecting its axis position. Values landing at/near the origin are nudged outward (display-only) so they don't stack at the shared center. Charts are interactive HTML — hover a point for its full id/label/description, click a legend entry to toggle a dimension.
>
> **Caveat:** merge decisions are never made from the projected 2D/3D coordinates — only from full-dimensional embedding distance. The PCA-reduced chart reports explained variance and flags itself as a weak proxy when captured variance is low.

### 2.9 Evaluation

| YAML Key | Type | Default | Description |
|---|---|---|---|
| `evaluation.enabled` | `bool` | `true` | Master on/off switch for the taxonomy evaluation scoreboard (deepeval GEval). When `false`, the `evaluate_taxonomy` node is skipped and the pipeline topology matches pre-evaluation behavior exactly. |
| `evaluation.judge_model` | `str` or `null` | `null` | Judge model override in `provider/model` format. Falls back to `models.model`. OpenAI (or OpenAI-compatible) models only — deepeval's built-in OpenAI integration is used directly; a non-OpenAI provider raises a clear error naming the documented future-wrapper path (`evaluation/judge.py`). |
| `evaluation.threshold` | `float` | `0.5` | Display-only pass threshold (0-1) per criterion. Pass flags never gate anything — the scoreboard is observe-only. |
| `evaluation.consistency_threshold` | `float` | `0.25` | Embedding-distance cutoff (Euclidean on L2-normalized vectors) below which dimensions from different taxonomies align automatically during consistency comparison. |
| `evaluation.consistency_borderline_band` | `float` | `0.08` | Distance band above the cutoff routed to judge adjudication instead of auto-align or auto-reject. |
| `evaluation.max_documents` | `int` | `20` | Max documents sampled for the data-grounded coverage criterion. Without documents the coverage row is listed as "not evaluated". |

> **Scoreboard semantics:** seven criteria judged via deepeval `GEval` — six structural (orthogonality, clarity, completeness, use case alignment, no catch-alls, axis vs. value) judged against the use case, plus one data-grounded coverage criterion judged against sampled document contents. Each row carries a 0-1 score, pass flag, and the judge's rationale. Anonymous deepeval telemetry is always opted out programmatically.

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
| `--taxonomy` | `str` | `None` | Yes (with `--mode test`) | Path to a saved taxonomy JSON to start from (its final iteration is seeded as the starting taxonomy). Sets `pipeline.taxonomy_input`. |

### 4.2 Configuration

| Argument | Type | Default | Description |
|---|---|---|---|
| `--config` | `str` | `None` (uses `./config.yaml`) | Path to a YAML configuration file. If not provided, defaults to `./config.yaml` in the project root. |

### 4.3 Run Mode

| Argument | Type | Default | Description |
|---|---|---|---|
| `--mode` | `{train, test}` | `train` | Run mode. `train` builds/updates the taxonomy progressively. `test` freezes the seeded taxonomy's dimensions and only labels new documents against them. Sets `pipeline.mode`. Requires `--taxonomy`. |

### 4.4 Feedback

| Argument | Type | Default | Description |
|---|---|---|---|
| `--feedback` | `str` | `None` | Feedback text injected into taxonomy refinement prompts (update/review). Mutually exclusive with `--feedback-file`. |
| `--feedback-file` | `str` | `None` | Path to a text/markdown file with feedback for taxonomy refinement. Mutually exclusive with `--feedback`. |

### 4.5 Taxonomy

| Argument | Type | Default | Description |
|---|---|---|---|
| `--name` | `str` | `None` | Override the taxonomy name (`taxonomy.name`). Shown in CLI output and included in JSON files. |

### 4.6 Model Overrides

| Argument | Type | Default | Description |
|---|---|---|---|
| `--model` | `str` | `None` | Override the main LLM model (`models.model`). Format: `provider/model-name`. |
| `--fast-model` | `str` | `None` | Override the fast LLM model (`models.fast_llm`). Format: `provider/model-name`. |

### 4.7 Output

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
| Loop termination | `saturation_streak >= threshold` OR `num_revisions >= num_minibatches` | Stops early on theoretical saturation; otherwise runs once per minibatch. The `saturation_streak_threshold` itself is configurable (`taxonomy.saturation_streak_threshold`). |
| Batch scheduling | `open_code_batch_index - 1` | The update consumes the minibatch just open-coded (no round-robin cycling). |

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
| `user_feedback` | `UserFeedback` | `None` | Supports `"continue"` or `"modify"` decisions. Can be seeded externally via `--feedback`/`--feedback-file`/`feedback.*` config (resolved in `main.py`). |
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
| **Models** | Embedding model | `models.embedding` | `openai/text-embedding-3-small` |
| **Pipeline** | Max documents to process | `pipeline.max_runs` | `500` |
| **Pipeline** | Documents to sample | `pipeline.sample_size` | `50` |
| **Pipeline** | Minibatch size | `pipeline.batch_size` | `200` |
| **Pipeline** | Random seed | `pipeline.random_seed` | `42` |
| **Pipeline** | Run mode | `pipeline.mode` | `"train"` |
| **Pipeline** | Starting taxonomy JSON path | `pipeline.taxonomy_input` | `null` |
| **Taxonomy** | Taxonomy name | `taxonomy.name` | `"taxonomy"` |
| **Taxonomy** | Use case description | `taxonomy.use_case` | User intent classification |
| **Taxonomy** | Max categories | `taxonomy.max_num_clusters` | `25` |
| **Taxonomy** | Max name length (words) | `taxonomy.cluster_name_length` | `10` |
| **Taxonomy** | Max description length (words) | `taxonomy.cluster_description_length` | `30` |
| **Taxonomy** | Max suggestion length (words) | `taxonomy.suggestion_length` | `30` |
| **Taxonomy** | Max explanation length (words) | `taxonomy.explanation_length` | `20` |
| **Taxonomy** | Saturation streak threshold | `taxonomy.saturation_streak_threshold` | `2` |
| **Taxonomy** | Value merge distance threshold (epsilon) | `taxonomy.value_merge_distance_threshold` | `0.2` |
| **Taxonomy** | Value merge borderline band | `taxonomy.value_merge_borderline_band` | `0.08` |
| **Taxonomy** | Review sample size | `taxonomy.review_sample_size` | `null` (uses `batch_size`) |
| **Taxonomy** | Value consolidation enabled | `taxonomy.consolidate_values` | `true` |
| **Feedback** | Inline feedback text | `feedback.text` | `null` |
| **Feedback** | Feedback file path | `feedback.file` | `null` |
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
| **Visualization** | Enabled | `visualization.enabled` | `false` |
| **Visualization** | Render every iteration | `visualization.every_iteration` | `false` |
| **Visualization** | PCA dimensions | `visualization.dimensions` | `2` |
| **Visualization** | Chart output directory | `visualization.output_dir` | `null` (uses `output.default_output_dir`) |
| **Evaluation** | Evaluation enabled | `evaluation.enabled` | `true` |
| **Evaluation** | Judge model override | `evaluation.judge_model` | `null` (uses `models.model`; OpenAI models only — see below) |
| **Evaluation** | Display pass threshold (0-1) | `evaluation.threshold` | `0.5` |
| **Evaluation** | Consistency alignment threshold | `evaluation.consistency_threshold` | `0.25` |
| **Evaluation** | Consistency borderline band | `evaluation.consistency_borderline_band` | `0.08` |
| **Evaluation** | Max documents for coverage criterion | `evaluation.max_documents` | `20` |

### 🎯 Standalone evaluation command

```bash
# Judge scoreboard for one saved taxonomy (coverage "not evaluated" without --corpus):
python main.py --evaluate <path/to/taxonomy.json> [--corpus <path>] [--output DIR]

# With a corpus (activates the data-grounded coverage criterion):
python main.py --evaluate <taxonomy.json> --corpus <corpus.json|corpus.txt> [--config <cfg.yaml>] [--output DIR]

# Consistency comparison across two or more saved taxonomies (same corpus):
python main.py --evaluate <tax1.json> <tax2.json> [<tax3.json> ...] [--output DIR]
```

Evaluates saved taxonomy JSONs without re-running the pipeline. One file runs the judge scoreboard (optionally with `--corpus`, which activates the coverage criterion; `--iteration N` selects the view exactly as in `--visualize`/`--report`); two or more files run the consistency comparison (embedding-based dimension alignment with judge adjudication of borderline pairs, reporting recurring dimensions, one-offs, and an agreement score). Results render in the terminal and are saved as `{name}_evaluation_{timestamp}.json`. Mutually exclusive with `--visualize` and `--report`.

### 📊 Standalone biplot command

```bash
python main.py --visualize <path/to/taxonomy.json> [--iteration N] [--axis-positions {auto,embeddings,uniform}] [--output DIR]
```

Renders a PCA biplot from a saved taxonomy JSON without running the pipeline. Cluster source: `--iteration N` (1-based) > `selected_clusters` > last iteration. `auto` follows the `consolidated` flag recorded in the file (uniform for legacy files — fully offline); `uniform` places every value of a dimension at unit distance (no API calls); `embeddings` computes axis positions from the embedding model.

### ✅ Configurable via CLI / Env

| Setting | CLI Flag | Env Var | Config YAML Key |
|---|---|---|---|
| Taxonomy name | `--name` | — | `taxonomy.name` |
| Main model | `--model` | `LLM_MODEL` | `models.model` |
| Fast model | `--fast-model` | `LLM_FAST_MODEL` | `models.fast_llm` |
| Run mode | `--mode` | — | `pipeline.mode` |
| Starting taxonomy | `--taxonomy` | — | `pipeline.taxonomy_input` |
| Feedback (inline) | `--feedback` | — | `feedback.text` |
| Feedback (file) | `--feedback-file` | — | `feedback.file` |
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