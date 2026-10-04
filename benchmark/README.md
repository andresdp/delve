# ADD-Bench sources

Gray-literature corpora of the published Straussian-GT ADD studies used to evaluate DelveDSpace
(see `docs/paper/SANER2027_PAPER_PLAN.md`, §4 and backlog item B2).

| Case | Study | Sources | Where the URLs come from |
|---|---|---|---|
| `c1-ml-workflow/` | Warnett & Zdun, *Architectural Design Decisions for the Machine Learning Workflow* (IEEE Software, 2021/22) | 29 | Paper Table 1: `tinyurl.com/ml-adds-u1…u29`, each resolving to the authors' June 2021 Wayback Machine snapshot |
| `c2-rl-monitoring/` | Fang, Warnett & Zdun, *Architectural Design Decisions for Monitoring Deployed Reinforcement Learning Systems* (2026) | 29 | `**URL**` line of each source memo in the replication package (Zenodo 10.5281/zenodo.20305497, Apache-2.0), copied to `c2-rl-monitoring/replication_package/` |

The full list of URLs is in [`SOURCE_URLS.md`](SOURCE_URLS.md).

## Layout per case

- `sources.csv`: id, title, source type, paper class, original URL, archive URL/timestamp, fetch override, notes.
- `sources/raw/<id>.html|pdf`: downloaded bytes (gitignored).
- `sources/text/<id>.md`: extracted main text with a provenance header (gitignored).
- `sources/manifest.json` / `manifest.csv`: per-source provenance (fetched URL, via, HTTP status, SHA-256,
  word count, quality flags, all attempts).

## Re-creating the corpora

```bash
conda activate taxonomy   # needs httpx, trafilatura, beautifulsoup4, lxml + poppler's pdftotext
python benchmark/fetch_sources.py                       # both cases (C1, then C2)
python benchmark/fetch_sources.py benchmark/c1-ml-workflow   # one case only
# re-fetch selected sources:
python benchmark/fetch_sources.py benchmark/c2-rl-monitoring --only s19 --force
```

Fetch order: `fetch_override` → the authors' archived snapshot (raw `id_` mode) → live URL → closest
Wayback snapshot. Sources flagged `short`, `paywall` or `bot_block` in the manifest need a manual check.

## Building the DelveDSpace corpora

```bash
python benchmark/build_corpus.py          # writes examples/<case>/<case>_corpus.json for C1 and C2
```

`build_corpus.py` strips the provenance header and markdown noise (links, images, URLs, empty bullets,
ligatures; PDF text is reflowed) and splits each source into passages of about 300 words at paragraph and
heading boundaries (code blocks are never split; passages under 80 words are merged into a neighbour).
Each passage is one DelveDSpace document with id `sNN_pKK`. Run configs and instructions are in
`examples/c1-ml-workflow/` and `examples/c2-rl-monitoring/`.

## Verification status (2026-10-01)

Checks:
- expected title present;
- boilerplate and junk markers;
- for C2, presence of the analysts' quotes (the "Open Codes & Quotes" lines in `replication_package/memos/sNN.md`)
  in the downloaded text, scored fuzzily (at least 70% of a quote's content words present);
- manual skim of the beginning and end of every text.

| Case | Usable | Words (≈ tokens) | Notes |
|---|---|---|---|
| C1 | 29/29 | 70k (≈ 95k) | All from the authors' 2021 snapshots. s4 includes the full talk transcript. s8 (slides) is fragmented and partly marketing, but usable |
| C2 | 27/29 | 62k (≈ 84k) | 23 texts contain 100% of the analysts' quotes; s2, s27, s28 contain 80–92% (minor live-page drift). s3 and s16 were saved manually from a browser (`via: manual`) |

Cleanup applied by the extractor (re-run offline with `--reextract`):
- removed reference lists, "See also" / "Further reading", "Related content" blocks, and an SEO keyword appendix
  (C2 s4) (`removed_sections` in the manifest);
- dropped LessWrong comment threads (C2 s25, s26; all quotes are in the post body);
- added site extractors for StackExchange (question + answers, C2 s17) and LinkedIn (list items, C2 s19).

**Manual action needed (C2):**

| Source | Problem | Suggested fix |
|---|---|---|
| s5 (Medium) | 403 bot block; no Wayback snapshot (s3 and s16 already done manually) | Open in a browser and save the page (or copy the article text) as `sources/raw/sNN.html`, then run `--reextract --only sNN` |
| s10 (nexastack) | Live page gone (404); the Wayback copy is a redirect stub, so the text is empty | Retry with `--only s10 --force` once the Internet Archive CDX service is back (it was temporarily offline), or try archive.today |

Known content issue (left as is, because it is what the analysts coded): C2 s4 is machine-generated SEO content
(headings such as "(TABLE REQUIRED)").

## Caveats

- **C1 uses the authors' archived copies (2021)**: what the analysts saw.
- **C2 uses live pages (retrieved 2026-10)** with a Wayback fallback. The analysts coded them in early 2026,
  so pages may have changed since; compare against the memos in `replication_package/memos/` if in doubt.
- Source texts are third-party content: they are not committed, and only URLs and scripts are released.

## Evaluation frame

What every ground-truth score rests on, fixed **before any run was scored** (R13). The frame is fixed at the
commit that adds this section (`git log -- benchmark/README.md`); any later change is logged under "Changes"
below, with the date and the reason. There are no hashes: the commit history is the record.

### Use cases

The use case each system run receives is `taxonomy.use_case` of the study's config, as committed at
`afebe10` (2026-10-02):

- **C1:** `examples/c1-ml-workflow/c1_ml_workflow_config.yaml`. The architectural design decisions of ML
  systems along the ML workflow, from data ingestion and processing through model building and training to
  production and operation, with options, forces and relations, from gray literature.
- **C2:** `examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml`. The architectural design decisions for
  monitoring deployed RL agents, with options, forces and relations, from gray literature.

Both name one design decision per dimension, with its options as values.

**Agreed by:** *pending; two authors confirm the use cases here (name, date) before the scores are
reported.*

### Ground truth and views

`benchmark/<study>/gt/`; see each study's README for sources, counts and discrepancies.

| Study | Views scored | Options (attached) |
|---|---|---|
| C1 | paper (Table 2), model (Zenodo 10.5281/zenodo.5730291) | paper 43, model 121 |
| C2 | paper, model (Zenodo 10.5281/zenodo.20305497) | paper 57, model 62 |

Unattached model options are excluded. Matching runs once against the union of a study's views; metrics are
computed per view.

### Metric definitions

| Level | Definition |
|---|---|
| **Pair labels** | Each pair of a system candidate value and a ground-truth option gets one label: `same`, `broader` (the value is more general), `narrower`, `related` or `different`. |
| **Option level** (primary) | A hit is `same`, `broader` or `narrower`. **Precision**: share of system candidate values with a hit in the view. **Recall**: share of the view's options with a hit. **F1**: their harmonic mean. **Exact-option recall**: recall counting only `same`. **Related rate**: share of system values whose best label is `related`. |
| **Decision level** | Alignment of system dimensions and expert decisions. Each pair has a share: the matched values and options between the two, over the smaller of their counts. Ties are broken by embedding distance. **Strict alignment**: one-to-one (`linear_sum_assignment`) over pairs with share ≥ `min_alignment_share`. **Lenient alignment**: every pair above that share (splits and merges count). Precision, recall and F1 are reported for each. |
| **Placement** | Among matched values, the share whose dimension is aligned (lenient) with a decision that their matched option belongs to. |

Outcome values are excluded from the system side (the candidates-only decision); a sensitivity run may
include them (`matcher.include_outcomes`).

**Per-view rules:**
- Recall in a view counts only that view's options and decisions.
- Paper-view precision leaves out system values matched only to `model only` options, and reports how many
  there are.

### Matcher settings

| Setting | Value | How it was chosen |
|---|---|---|
| Serialization | `<decision or dimension> › <option or value>: <description>`, CamelCase split | paper plan §5.1 M1 |
| Embedding model | `openai/text-embedding-3-small` | the pipeline's embedding model |
| Distance | cosine distance (1 − cosine similarity); lower is closer | user decision (2026-10-03) |
| `lower_threshold` | **0.0**: no pair is labeled `same` without the judge | ground truth only (below) |
| `upper_threshold` | **0.60**: pairs farther apart are `different` without the judge | ground truth only (below) |
| `max_candidates` | **5**: a borderline pair reaches the judge only if one item is among the other's 5 nearest | bounds judge calls |
| Judge | the pipeline's `evaluation.judge_model` (or `matcher.judge_model`), never the generator (`models.model`); test runs use **`openai/gpt-5.4-mini`**; generator of the scored runs: `openai/gpt-5.6-luna` | user decision (2026-10-03): only OpenAI is available, so independence is partial; the judge is validated against human gold alignment later (A6) |
| Judge instructions | `gt_match.JUDGE_STEPS` (version hash in every output). The judge compares the options regardless of their decisions; the two items appear as "Item 1" and "Item 2" in a seeded order, never as system or ground truth | plan KTD7 |
| `seed` | 0 | – |

**How the thresholds were chosen**, without looking at any system output (`python
benchmark/frame_thresholds.py --config examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml`, 2026-10-03):
- the 184 attached ground-truth options (C1 121, C2 63) were embedded with the serialization above;
- **Distinct options of the same study** (9,213 pairs): min 0.031, p1 0.177, p5 0.326, median 0.611.
  - The closest pairs are *opposite* options of one decision with short descriptions: "No AutoML" vs.
    "AutoML" (0.031), "Batch-based" vs. "Real-time" processing (0.047), "MLOps" vs. "No MLOps" (0.069).
  - The shared decision prefix dominates. No distance cutoff separates `same` from `different`, so
    `lower_threshold` is 0: every `same` comes from the judge.
- **Options of different studies** (7,623 pairs; ML workflow vs. RL monitoring, so unrelated): min 0.416,
  p0.5 0.536, p1 0.564, p2 0.600, p5 0.650.
  - `upper_threshold` is 0.60, their 2nd percentile. Pairs farther apart than nearly all unrelated pairs are
    labeled `different` without the judge.

**Unjudged pairs:** every pair keeps its label source.
- `auto`: beyond the upper threshold.
- `auto_rank`: a borderline pair outside both items' nearest neighbours.
- `judge`: labeled by the judge.

A pair labeled `different` without the judge is *unjudged*, not judged wrong. The candidate-recall check (paper
plan §5.1 M9, A6) measures how many true matches the automatic labels miss.

### Runs to score

The first scored runs are the DelveDSpace runs of 2026-10-02:
- `examples/c1-ml-workflow/c1-ml-workflow_taxonomy_20261002_185546.json`;
- `examples/c2-rl-monitoring/c2-rl-monitoring_taxonomy_20261002_211657.json`.

Both are scored on their selected view.

### Changes after scores were seen

*None yet.*
