# Delve: replication package

*Anonymized for review.*

This package accompanies the paper on Delve, an agentic workflow that mines architectural design spaces from
practitioner literature with grounded-theory techniques. It contains:
- the implementation, exactly as it produced the paper's runs;
- the evaluation kit: source inventories, expert models, crosswalks and the matcher;
- the configurations of every run;
- the stored outputs of every run reported in the paper;
- the scripts that turn those outputs into the paper's tables.

**Every number in the paper can be recomputed from the stored runs without API calls.**
See [REPRODUCE.md](REPRODUCE.md), which also maps each table to its command.

## Contents

| Path | What |
|---|---|
| `src/taxonomy_generator/` | The workflow (LangGraph): Coder (open coding), Taxonomist (validated editing operations), Critic (scoreboard and saturation check), consolidation, selection, evidence linking. Prompts in `prompts/`. |
| `src/delvedspace/` | Command-line front end (`ddspace`) and wiki builder |
| `main.py`, `config.yaml` | The pipeline's command line and the default settings |
| `examples/c1-ml-workflow/`, `examples/c2-rl-monitoring/`, `examples/c3-git-at-scale/` | The configuration of each case and variant (full, no critic feedback, whole-model rewriting; C3 sample and curated) |
| `examples/cursor-git-at-scale/` | The 16 curated write-ups behind C3's curated sensitivity corpus |
| `examples/c3-git-at-scale/sample/` | A published C3 run with its browsable design-space wiki (open `…_wiki/html/index.html`) |
| `benchmark/c1-ml-workflow/`, `benchmark/c2-rl-monitoring/` | Source inventories (`sources.csv`, manifests with SHA-256), both expert-model views (`gt/gt_paper.json`, `gt/gt_model.json`) and their crosswalk |
| `benchmark/c2-rl-monitoring/replication_package/` | The C2 study's published replication package (Apache-2.0), from which the model view is parsed |
| `benchmark/c3-git-at-scale/` | C3 source inventory, passage-to-system map and stated trade-offs |
| `benchmark/*.py` | Corpus retrieval and building, run matrix, baselines, matcher thresholds, analysis scripts |
| `output/evaluation/` | The stored runs (`runs.csv` lists them) and the analysis outputs (`report/`) |
| `tests/` | Unit tests, no API calls: `OPENAI_API_KEY=dummy python -m pytest tests/unit_tests`. `test_run_matrix.py::test_matrix_rows_point_at_existing_configs_and_corpora` passes only once the corpora are built (REPRODUCE.md, level 3, step 1). |

**Source texts are not redistributed** (copyright). `benchmark/fetch_sources.py` retrieves them from the URLs and
archive snapshots in `sources.csv`; the manifests record the SHA-256 of every retrieved file.

## Install

Python 3.10 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

New runs, and the LLM-judged checks, need an OpenAI key in `.env` (see `.env.example`). Recomputing the tables
from the stored runs needs none.

## License

MIT (see `LICENSE`). The C2 replication package keeps its own license.
