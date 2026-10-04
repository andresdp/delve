<p align="center">
  <img src="images/delvedspace-icon.svg" alt="DelveDSpace" width="96">
</p>

# Configuring and running DelveDSpace

How to prepare a corpus, configure a run, use the command line, read the outputs and the evaluation, and
call DelveDSpace from Python. For what DelveDSpace is, how the pipeline works and how to install it, see the
[README](README.md).

- [Preparing a corpus](#preparing-a-corpus)
- [Configuration](#configuration)
- [Command-line reference](#command-line-reference)
- [Outputs](#outputs)
- [Evaluation](#evaluation)
- [Using DelveDSpace from Python](#using-delvedspace-from-python)

## Preparing a corpus

- **`.txt`**: one document per line.
- **`.json`**: a list of strings, or a list of objects `{"id": "...", "content": "..."}`. Ids are kept,
  so evidence and labels refer to your own document ids.
- **Passages of longer sources:** split long documents into passages of a few hundred words with ids
  like `s03_p02` (source 3, passage 2). DelveDSpace then counts evidence per source as well as per passage,
  and the minimum-support rule works on sources.

## Configuration

All settings live in one YAML file, passed with `--config` (default: `./config.yaml`). The repository's
[`config.yaml`](config.yaml) documents every setting inline and is the reference to copy from.

| Section | What it controls |
|---|---|
| `models` | Three LLM roles, which should be different models (a shared model runs with a warning): `generation_llm` builds the design space (open coding, summaries, generation, update, review, consolidation, merging, selection, labeling, report text); `evaluation_llm` judges it in the pipeline (scoreboard, consistency comparison, saturation critic); `matching_llm` judges value-option pairs in ground-truth matching (`--match-gt`). Plus `embedding` (consolidation, evidence linking, dimension merging, biplots, matching candidates) |
| `pipeline` | `batch_size` (documents per minibatch), `random_seed`, `mode` (`train` / `test`), `taxonomy_input` and `taxonomy_input_view` (start from a saved run) |
| `taxonomy` | `use_case` (**the most important setting**), `name`, `max_num_clusters` (`null` = no cap), saturation, value consolidation, evidence linking, fragmentation controls |
| `feedback` | Your own feedback text or file, injected into update and review prompts |
| `summarization` | Summarize documents first, or `skip: true` to work on the raw text |
| `open_coding` | `input`: code from summaries or from the full text |
| `labeling` | Fallback category name, review sample size |
| `evaluation` | Judge on/off, judge model, pass threshold, `every_n_iterations`, `feedback_exclude`, `save_history`, sample size for the data-grounded criteria |
| `visualization` | PCA biplots on/off, per iteration or final only |
| `output` | Display limits, default output folder |

Settings to look at first:

- **`taxonomy.use_case`**: what the design space is for, e.g. *"Identify the architectural design
  decisions practitioners face when … For each decision, identify the alternative options …"*. It
  steers coding, selection and evaluation.
- **`taxonomy.max_num_clusters`**: prefer `null`. A hard cap forces broad topics that bundle several
  decision points.
- **Saturation:**
  - `saturation_streak_threshold`: saturated minibatches in a row needed to stop;
  - `saturation_min_coverage`: share of a minibatch's codes that must be covered to count as
    saturated;
  - `saturation_min_corpus_fraction`: minimum share of the corpus to read before stopping.
- **Fragmentation and evidence:**
  - `merge_dimensions`: merge near-duplicate decision points;
  - `min_dimension_sources`: minimum number of supporting sources per decision point;
  - `min_candidate_decisions`: minimum candidate decisions per decision point;
  - `link_evidence`, `drop_unsupported_values`: link codes to values, and drop values with no evidence.
- **Cost:**
  - `evaluation.every_n_iterations`: e.g. 3 for corpora with many minibatches;
  - `evaluation.enabled: false`: skip the judge for cheap smoke tests.

Command-line flags override a few settings: `--generation-llm`, `--evaluation-llm`, `--matching-llm`, `--name`, `--max-clusters`,
`--mode`, `--taxonomy`, `--feedback`, `--feedback-file`.

## Command-line reference

### Running the pipeline

| Flag | Purpose |
|---|---|
| `--corpus PATH` | Corpus file (`.txt` or `.json`) |
| `--config PATH` | YAML configuration (default `./config.yaml`) |
| `--output DIR` | Save all artifacts to `DIR` (created if missing); also writes the Markdown report unless `--no-auto-report` |
| `--mode train\|test` | `train` builds or refines a design space; `test` freezes the dimensions of `--taxonomy` and labels new documents |
| `--taxonomy PATH` | Saved taxonomy JSON to start from (required in test mode) |
| `--feedback TEXT`, `--feedback-file PATH` | Feedback for the update and review prompts, e.g. a critique of a previous run |
| `--generation-llm`, `--evaluation-llm`, `--matching-llm` | Override the LLM roles (`provider/model-name`) |
| `--name`, `--max-clusters` | Override the taxonomy name and the dimension cap |
| `--quiet` | Hide logs, show only the result panels |

Refining a previous run with your feedback:

```bash
python main.py --corpus my_corpus.json --config my_project.yaml --output results/ \
               --taxonomy results/myproject_taxonomy_<timestamp>.json \
               --feedback "Split 'Deployment strategy' into rollout and rollback decisions."
```

Labeling new documents against a saved design space:

```bash
python main.py --mode test --taxonomy results/myproject_taxonomy_<timestamp>.json \
               --corpus new_documents.json --config my_project.yaml --output results/
```

### Working with saved runs (no pipeline run)

```bash
# Markdown grounded-theory report (narrative, relation diagram, value catalog, dropped dimensions)
python main.py --report results/myproject_taxonomy_<timestamp>.json

# Single-page offline HTML report (run summary, relation diagram, value catalog, dropped dimensions, narrative, biplot, scoreboard)
python main.py --html-report results/myproject_taxonomy_<timestamp>.json

# PCA biplot of values on dimension axes (--axis-positions auto|embeddings|uniform)
python main.py --visualize results/myproject_taxonomy_<timestamp>.json

# Score a saved design space; --corpus enables the data-grounded criteria
python main.py --evaluate results/myproject_taxonomy_<timestamp>.json --config my_project.yaml --corpus my_corpus.json

# Score every saved iteration with the current criteria
python main.py --evaluate results/myproject_taxonomy_<timestamp>.json --all-iterations --config my_project.yaml --corpus my_corpus.json

# Compare several runs on the same corpus (recurring vs. one-off dimensions)
python main.py --evaluate run1.json run2.json run3.json --config my_project.yaml

# Score a saved design space against an expert ground truth (precision, recall, F1 and Jaccard of
# options and decisions, placement; per ground-truth view). The matching LLM judges borderline
# value-option pairs; --matcher-mode embeddings uses embedding distance alone (no LLM calls).
python main.py --match-gt results/myproject_taxonomy_<timestamp>.json --gt benchmark/c2-rl-monitoring/gt --config my_project.yaml
```

`--iteration N` renders or scores a specific iteration instead of the selected view.

## Outputs

With `--output DIR`, files are named `<name>_<kind>_<timestamp>` (the name comes from
`taxonomy.name` or `--name`):

| File | Content |
|---|---|
| `<name>_taxonomy_<ts>.json` | **Main result**: every iteration, the selected dimensions with values, stances, evidence and relations, the dropped dimensions with reasons, the saturation history, the evaluation scoreboard and its history, run metrics (time, tokens) |
| `<name>_report_<ts>.md` | Grounded-theory report of the selected view |
| `<name>_documents_<ts>.json` | Documents with summary, assigned dimension and value, confidence score |
| `<name>_clusters_<ts>.json` | The selected design space as a tree with the labeled documents nested in it |
| `<name>_open_codes_<ts>.json` | All open codes (document id, label, rationale, status) |
| `<name>_messages_<ts>.json` | Pipeline messages |
| `<name>_html_report_<ts>.html` | From `--html-report` |
| `<name>_evaluation_<ts>.json` | From `--evaluate` |

The documents, clusters, messages and HTML files contain the corpus text; keep that in mind before
committing them.

## Evaluation

Each scoreboard scores ten criteria (0–1) with an LLM judge using fixed judging steps:

- **Structure:**
  - Orthogonality, Clarity, Completeness, Use case alignment, No catch-alls;
  - Axis vs. value;
  - One decision point (with quality-attribute grounding as a secondary preference);
  - Rejected-alternative handling.
- **Data-grounded** (on a fixed sample of documents spread across sources):
  - Dimensional coverage;
  - Candidate-decision coverage.

Each criterion comes with a reason that names the dimensions and values at fault and the change that
would fix them. During the loop, the weakest criteria and their reasons are passed to the next update
and to the review. Completeness is scored but not fed back by default, since the judge sees no data for
it.

Judge scores are noisy (differences of ±0.1–0.2 between iterations are common) and measure structure,
not correctness. Use them together with the evidence counts, the dropped-dimension reasons and, when
available, a comparison with an expert-built design space.

## Using DelveDSpace from Python

```python
import asyncio
from taxonomy_generator import graph, init_settings, docs_from_dicts

init_settings("my_project.yaml")
docs = docs_from_dicts([
    {"id": "s01_p01", "content": "We moved from batch scoring to an online model server because ..."},
    {"id": "s02_p01", "content": "Canary releases let us compare the new model on 5% of traffic ..."},
])

result = asyncio.run(graph.ainvoke({"documents": docs}))
design_space = result["selected_clusters"][-1] if result["selected_clusters"] else result["clusters"][-1]
labeled = result["documents"]
scoreboard = result["evaluation"]
```

`strings_to_docs([...])` converts plain strings, with generated ids. The graph is also registered in
[`langgraph.json`](langgraph.json) for LangGraph Studio.
