# C2 — ADDs for Monitoring Deployed RL Systems (ADD-Bench case)

DelveDSpace run folder for the SANER 2027 evaluation (see `docs/paper/SANER2027_PAPER_PLAN.md`).
Ground truth: Fang, Warnett & Zdun, 2026. Corpus: 27 of 29 sources (s5, s10 unavailable), 243 passages of ~300 words each.

## Build the corpus

The corpus is built from the downloaded gray-literature sources (`benchmark/c2-rl-monitoring/sources/`):

```bash
conda activate taxonomy
python benchmark/build_corpus.py c2-rl-monitoring
```

This writes `c2-rl-monitoring_corpus.json` (gitignored: third-party text) and `c2-rl-monitoring_passages.csv`
(index without text). Passage ids look like `s03_p02` (source 3, passage 2), so every open code,
value and label stays traceable to its source.

## Run DelveDSpace

All commands run from the repository root, in the `taxonomy` conda env. The OpenAI API key is read
from the repository's `.env` file.

**1. Activate the environment and go to the repository root**

```bash
conda activate taxonomy
cd ~/Documents/GitHub/delve
```

**2. Build the corpus (only if `examples/c2-rl-monitoring/c2-rl-monitoring_corpus.json` is missing)**

```bash
python benchmark/build_corpus.py c2-rl-monitoring
```

**3. Run the pipeline**

```bash
python main.py --corpus examples/c2-rl-monitoring/c2-rl-monitoring_corpus.json \
               --config examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml \
               --output examples/c2-rl-monitoring/
```

The run open-codes all 243 passages in about 13 minibatches of 20, builds and refines the
taxonomy until saturation (or until the minibatches run out), reviews and consolidates it, then labels
every passage. Add `--quiet` to see only the summary panels instead of the logs.

For a cheaper first smoke test, set `evaluation.enabled: false` in `c2_rl_monitoring_config.yaml` for that run. This skips the
LLM-as-judge scoreboard, which otherwise runs after every iteration. Set it back to `true` for the
real runs.

**4. Outputs** (in `examples/c2-rl-monitoring/`, all named `c2-rl-monitoring_<kind>_<timestamp>`)

- `c2-rl-monitoring_taxonomy_<timestamp>.json`: the design space, with every iteration, the saturation history,
  the selected dimensions and the evaluation scoreboard. This is the file compared against the ground truth.
- `c2-rl-monitoring_report_<timestamp>.md`: the grounded-theory report (written automatically).
- `c2-rl-monitoring_documents_…`, `_clusters_…`, `_messages_…`: run details (gitignored: they contain source text).
- `taxonomy_biplot_c2-rl-monitoring_*.html`, `taxonomy_vectors_c2-rl-monitoring_*.csv`: biplot and vectors.

**5. Optional: build the single-page HTML report for the latest run**

```bash
python main.py --html-report "$(ls -t examples/c2-rl-monitoring/c2-rl-monitoring_taxonomy_*.json | head -1)"
```

**6. Optional: compare repeated runs (e.g. different `random_seed` values)**

```bash
python main.py --evaluate examples/c2-rl-monitoring/c2-rl-monitoring_taxonomy_<timestamp1>.json \
                          examples/c2-rl-monitoring/c2-rl-monitoring_taxonomy_<timestamp2>.json
```

**7. Optional: scores across iterations, and re-scoring a past run**

With `evaluation.save_history: true` (the default), a run saves every evaluation scoreboard in `evaluation_history` of the taxonomy JSON (one per
iteration, then the final view) and prints them in an "Evaluation across iterations" table. To score
the saved iterations of an existing run with the current criteria (about 10 judge calls per
scored iteration; this config scores every 3rd draft, `evaluation.every_n_iterations: 3`):

```bash
python main.py --evaluate "$(ls -t examples/c2-rl-monitoring/c2-rl-monitoring_taxonomy_*.json | head -1)" \
               --all-iterations \
               --config examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml \
               --corpus examples/c2-rl-monitoring/c2-rl-monitoring_corpus.json
```

The data-grounded criteria are judged on the same 20 passages as during the run (drawn across sources
with the run's `random_seed`). Loop iterations are raw drafts; the selected view is consolidated, so
it is not directly comparable with them.

Key settings in `c2_rl_monitoring_config.yaml`:

- `open_coding.input: content`: open coding reads each full passage, never a summary.
- `summarization.skip: true`: passages are short, and labeling reads the full text anyway.
- `batch_size: 20`, `saturation_streak_threshold: 3`, `max_num_clusters: null`.
- Fragmentation controls:
  - `merge_dimensions: true`: near-duplicate dimensions are merged, judged by the LLM;
  - `min_dimension_sources: 2`: dimensions supported by a single source are dropped, with a rationale;
  - `saturation_min_coverage: 0.9`: a minibatch counts as saturated when 90% of its codes fit the taxonomy as it was before that minibatch (the minibatch the taxonomy was generated from is never counted).
  - `saturation_min_corpus_fraction: 0.7`: saturation can end the loop only after 70% of the passages
    have been open-coded (about 9 of 13 minibatches).
- `link_evidence: true`: each option's supporting passages are rebuilt from the open codes
  (saved per run as `*_open_codes_*.json`).
- `use_case`: written from the study's research questions and scope only (draft, to be agreed).

Outputs that embed source text (`*_documents_*`, `*_clusters_*`, `*_messages_*`, `*_html_report_*`)
are gitignored; the taxonomy JSON, Markdown report and biplots can be committed.
