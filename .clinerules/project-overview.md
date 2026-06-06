## Brief overview
Delve is a taxonomy generator pipeline that classifies unstructured text data using LLM-powered LangGraph workflows. This is a Python project implementing the TnT-LLM framework from Wan et al. (2024), with a CLI entry point (`main.py`) and a modular pipeline architecture under `src/taxonomy_generator/`.

## Project architecture
- **Entry point**: `main.py` — argparse CLI with async execution, rich-formatted output, and logging
- **Pipeline graph**: `src/taxonomy_generator/graph.py` — LangGraph `StateGraph` defining the taxonomy generation workflow
- **Nodes**: `src/taxonomy_generator/nodes/` — each pipeline step is a separate module (e.g., `runs_retriever.py`, `summary_generator.py`, `taxonomy_generator.py`, `taxonomy_updater.py`, `taxonomy_reviewer.py`, `doc_labeler.py`, `minibatches_generator.py`)
- **Routing**: `src/taxonomy_generator/routing/` — conditional edge logic (e.g., `should_review.py`)
- **State**: `src/taxonomy_generator/state.py` — TypedDict-based state definitions (`State`, `InputState`, `OutputState`, `Doc`)
- **Configuration**: `src/taxonomy_generator/configuration.py` — centralized config with `Configuration` class
- **Prompts**: `src/taxonomy_generator/prompts.py` — all LLM prompt templates as `ChatPromptTemplate`
- **Utilities**: `src/taxonomy_generator/utils.py` — shared helpers (model loading, parsing, XML formatting, chain invocation)

## Pipeline phases
- **Data Ingestion** (`get_runs`) — accepts direct corpus input or LangSmith retrieval (legacy)
- **Preprocessing** (`summarize`, `get_minibatches`) — creates document summaries and partitions into batches
- **Taxonomy Generation** (`generate_taxonomy`) — produces initial taxonomy from first minibatch
- **Iterative Refinement** (`update_taxonomy` loop) — refines taxonomy per minibatch via conditional edge
- **Quality Review** (`review_taxonomy`) — final review pass on random document sample
- **Classification** (`label_documents`) — assigns categories to all documents using the final taxonomy

## State management
- Three-tier model: `InputState` → `State` (internal) → `OutputState`
- `clusters` uses `operator.add` reducer (accumulates taxonomy iterations)
- `Doc` dataclass is the standard document representation with `id`, `content`, `summary`, `explanation`, `category`
- `invoke_taxonomy_chain()` in `utils.py` is the shared orchestrator for all taxonomy nodes

## Tech stack
- Python 3.9+ with `pyproject.toml` (setuptools build)
- LangGraph for workflow orchestration
- LangChain with `init_chat_model` for multi-provider LLM support (OpenAI, Anthropic, Fireworks, Groq, Ollama)
- `rich` for terminal output formatting (tables, panels, styled text)
- `python-dotenv` for environment variable management
- All prompts defined locally in `prompts.py` — no external prompt hub

## Environment variables
- `LLM_MODEL` — main reasoning model (default: `openai/gpt-5.4-nano`)
- `LLM_FAST_MODEL` — fast model for summaries/labeling (default: `openai/gpt-5.4-nano`)
- `OPENAI_API_KEY` — required for default OpenAI models
- `ANTHROPIC_API_KEY`, `FIREWORKS_API_KEY`, `GROQ_API_KEY` — optional alternative providers
- Ollama runs locally (no API key) — use `ollama/<model>` format (e.g., `ollama/llama3.2`)
- `LANGSMITH_API_KEY` — optional, for LangSmith tracing / legacy retrieval

## Key configuration defaults
- `batch_size=200`, `max_num_clusters=25`, `sample_size=50`, `max_runs=500`
- `cluster_name_length=10` words, `cluster_description_length=30` words

## CLI conventions
- Use `argparse` with grouped arguments: "Input source", "Model configuration", "Output"
- `--quiet` flag suppresses logging (sets level to WARNING), shows only rich-formatted output
- `--output` saves results (documents, taxonomy, messages) as timestamped JSON files
- `--corpus` accepts `.txt` (one doc per line) or `.json` (array of strings/objects with `content` field)
- Graph PNG is exported automatically when not in quiet mode
- Always display the LLM model names in rich output (visible even in quiet mode)

## Logging conventions
- Use `logging.getLogger(__name__)` in every module — never use bare `print()` for status info
- Log level INFO for pipeline progress, DEBUG for detailed internals, WARNING for recoverable issues, ERROR for failures
- Suppress `httpx` logger to WARNING level to avoid noisy HTTP request logs
- Logging configuration is set in `main.py` only — modules just get their own named logger

## Output formatting
- Use `rich` library for all user-facing terminal output in `main.py`
- Taxonomy results: `rich.table.Table` with styled borders, row striping, and summary footer
- Document labeling: `rich.table.Table` showing category + content preview (max 20 docs)
- Section headers: `rich.panel.Panel` with styled titles and borders
- Never use `title_style` parameter on `Panel` (not supported in all rich versions) — use inline markup in the `title` string instead
- `Table` supports `title_style` — use it freely
- Use emoji icons in output for visual distinction (🚀, 📊, 📄, 💾, ✅, etc.)

## Coding style
- Each LangGraph node is an async function accepting `(state, config)` and returning a `dict` of state updates
- Chain setup is extracted into a private `_setup_*_chain()` helper in each node module
- Use `Configuration.from_runnable_config(config)` to access settings inside nodes
- Model names follow `provider/model` format (e.g., `openai/gpt-4o-mini`)
- XML-based prompt formatting for LLM inputs (documents, taxonomy clusters)
- All LLM outputs parsed via regex from XML tags (`<cluster_table>`, `<category>`, `<summary>`, etc.)

## Dependencies
- Add new dependencies to both `pyproject.toml` and `requirements.txt`
- Use `pip install -e .` for development installs
- Keep `requirements.txt` in sync with `pyproject.toml` dependencies list