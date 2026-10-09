# C3 sample: Git at scale, 5 dimensions

A small, published snapshot of DelveDSpace's output for case C3. The case is how teams made Git repositories
work at scale: very many repositories, very large repositories and very many users. The snapshot exists to
show what the approach produces end to end:
- the design space;
- its evidence;
- the labeled passages;
- the reports;
- a browsable wiki.

It is **not** the study run. The study run of C3 is in the parent folder
(`../c3-git-at-scale_taxonomy_20261008_115350.json`). That run has no cap on the number of dimensions, and its
outputs that quote the corpus are not committed.

**Open the wiki:** [browse it online](https://raw.githack.com/andresdp/delve/main/examples/c3-git-at-scale/sample/c3-git-at-scale-sample_taxonomy_20261009_083607_wiki/html/index.html). It is served by raw.githack.com, because GitHub shows HTML
files as source. Alternatively, open
[`c3-git-at-scale-sample_taxonomy_20261009_083607_wiki/html/index.html`](c3-git-at-scale-sample_taxonomy_20261009_083607_wiki/html/index.html)
from a local clone; the wiki works offline. It has a graph view and a tree view, linked from every page.

## How it was produced

- **Corpus:** 48 passages of about 300 words each, from 5 publicly available sources:
  - Cursor's "Git at any scale" article, which also describes GitHub's, Google's and Microsoft's systems;
  - two GitHub Engineering posts on Spokes;
  - Microsoft's Scalar philosophy document;
  - the "Introducing Scalar" post.

  The sources are listed in [`benchmark/c3-git-at-scale/sources.csv`](../../../benchmark/c3-git-at-scale/sources.csv).
- **Settings:** [`../c3_git_at_scale_sample_config.yaml`](../c3_git_at_scale_sample_config.yaml). These are the C3
  study settings, except `max_num_clusters: 5` and the output folder. The LLM is `openai/gpt-5.6-luna` for
  generation, evaluation and matching, and the embedding model is `text-embedding-3-small`.
- **Run:** 2026-10-09, about 18 minutes and 1.27M tokens. The run kept 5 dimensions throughout. The final view
  has 175 values. Its overall evaluation score is 0.65.
- **Dimensions:** with only 5 allowed, each one is broad, with 20–42 values each. The uncapped study run found
  22 narrower dimensions in the same corpus.
- **Design points:**
  - 24 sampled points: attested, novel and control groups, with 2 or 3 dimensions each and 4 points per group
    and size;
  - each has a 2–3 sentence LLM description, labeled as generated in the wiki.
- **Source summaries:** come from `benchmark/c3-git-at-scale/source_summaries.json`, also labeled as generated.

## Files

| File | Content |
|---|---|
| `*_taxonomy_<ts>.json` | The main result: every iteration, the selected dimensions with values, stances, evidence and relations, the evaluation and its history, and the operation log |
| `*_report_<ts>.md` | Grounded-theory report: narrative summary, relation diagram, value catalog |
| `*_html_report_<ts>.html` | The same as a single offline HTML page, with the biplot and the scoreboard |
| `*_documents_<ts>.json` | Each passage with its assigned dimension and value |
| `*_clusters_<ts>.json` | The design space as a tree, with the labeled passages nested in it |
| `*_open_codes_<ts>.json` | All open codes (passage id, label, rationale, status) |
| `*_design_points.json`, `*_design_points_sheet.csv`, `*_design_points_descriptions.json` | The 24 sampled design points, a rating sheet, and their descriptions |
| `taxonomy_biplot_*.html`, `taxonomy_vectors_*.csv` | PCA biplot of the values, and their axis coordinates |
| `*_wiki/` | The design-space wiki: `html/` (open `index.html`), `wiki/` (Markdown, Obsidian-compatible) and `raw/run.json` |

The pipeline's message log is left out (it is gitignored).

## How to rebuild it

Run these from the repository root, in an environment with the project installed and `OPENAI_API_KEY` set. The
LLM calls make each run differ in its details.

```bash
# 1. Corpus (downloads the sources; the corpus file is not committed)
python benchmark/fetch_sources.py benchmark/c3-git-at-scale
python benchmark/build_corpus.py c3-git-at-scale

# 2. Pipeline run (LLM; about 20 minutes)
python main.py --corpus examples/c3-git-at-scale/c3-git-at-scale_corpus.json \
               --config examples/c3-git-at-scale/c3_git_at_scale_sample_config.yaml \
               --output examples/c3-git-at-scale/sample/
RUN=examples/c3-git-at-scale/sample/c3-git-at-scale-sample_taxonomy_<timestamp>

# 3. HTML report (no LLM)
python main.py --html-report $RUN.json --config examples/c3-git-at-scale/c3_git_at_scale_sample_config.yaml

# 4. Design points with descriptions (one short LLM call per point)
python benchmark/design_points.py $RUN.json --systems benchmark/c3-git-at-scale/passage_systems.csv --n 4 --describe

# 5. Wiki (no LLM)
python benchmark/export_wiki.py $RUN.json \
       --corpus examples/c3-git-at-scale/c3-git-at-scale_corpus.json \
       --sources benchmark/c3-git-at-scale/sources.csv \
       --systems benchmark/c3-git-at-scale/passage_systems.csv \
       --system-names benchmark/c3-git-at-scale/systems.csv \
       --design-points ${RUN}_design_points.json \
       --config examples/c3-git-at-scale/c3_git_at_scale_sample_config.yaml --evaluation
```

See [USAGE.md](../../../USAGE.md#exploring-a-run-as-a-wiki) for the wiki options.
