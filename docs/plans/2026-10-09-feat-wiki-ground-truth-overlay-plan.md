---
title: "feat: wiki content modes: LLM run, ground truth only, overlay"
type: feat
status: planned (not started)
date: 2026-10-09
related: >-
  benchmark/export_wiki.py, src/taxonomy_generator/wiki/model.py, src/taxonomy_generator/wiki/render.py,
  benchmark/gt_format.py, benchmark/gt_crosswalk.py, src/taxonomy_generator/evaluation/gt_match.py,
  docs/DESIGN_SPACE_EXPLORATION.md §13 (wiki export; §13.6 agent read access and §13.7 2D/3D view are sibling plans)
---

# Wiki content modes: LLM run, ground truth only, overlay

## Goal

Make the wiki content configurable at export time, with three modes (user decision, 2026-10-09):

| Mode | Shows | Needs |
|---|---|---|
| `llm` (default, today's behavior) | the design space mined by Delve for one run | the run |
| `gt` | the expert ground truth only, rendered as a design space | `--gt` (no run needed) |
| `overlay` | the run's design space plus the GT as an extra layer, with matches and misses | the run, `--gt`, and the run's matcher outputs |

The overlay shows which expert options a value matches, which expert decision a dimension aligns with, and what was
missed. It works only for runs scored with `--match-gt` (today C1 and C2). Every mode stays offline: no LLM calls.

## Status of the exploration (2026-10-09)

Explored only; no code changed. All inputs already exist for the two runs whose wikis were exported on 2026-10-09:

- C1: `examples/c1-ml-workflow/u7/c1-u7b-tools_taxonomy_20261005_122709.json`
- C2: `examples/c2-rl-monitoring/u7/c2-u7b-tools-norelevance_taxonomy_20261005_110747.json`

Both were exported with `--core-min-sources 10` and source summaries (see "Re-export commands" below).

## Inputs (already on disk)

| Data | Files | Contents |
|---|---|---|
| Expert GT, two views | `benchmark/<case>/gt/gt_paper.json`, `gt_model.json` | `decisions`, `options` (with `decision_ids`; model view has `unattached` options), `forces`, `decision_forces`, `impacts`, `decision_links`; each item has a `source` (e.g. "Table 2 (p. 5)", `add_models/ml_adds.py:191`) and a `provenance` block |
| View relation | `benchmark/<case>/gt/gt_crosswalk.csv` | `kind,id,name,status,note`; status such as "both" / "model only" |
| Value ↔ option pairs | `<run>_gt_match.json` | `settings`, `label_sources`, `pairs[]` with `system_id` (value id, e.g. `39.1`), `gt_id`, `label` (same / broader / narrower / related / different), `label_source` (auto, auto_rank, judge), `reason`, `distance` |
| Dimension ↔ decision alignment | `<run>_gt_alignment.csv` | `view,alignment,dimension_id,dimension_name,decision_id,decision_name,share,matched`; alignment strict (Hungarian) or lenient |
| Scores | `<run>_gt_metrics.json` | per view: `option` (P/R/F1, tp counts, exact recall, related rate, …), `decision` (strict, lenient, jaccard), `placement` |

GT sizes:

| | C1 paper | C1 model | C2 paper | C2 model |
|---|---|---|---|---|
| Decisions | 10 | 28 | 7 | 7 |
| Options | 43 | 186 (121 attached to a decision) | 57 | 63 (62 attached) |
| Forces / impacts | 30 / 151 | 104 / 737 | 0 / 0 | 43 / 150 |
| Decision links | 0 | 40 | 6 | 6 |

Match file sizes: C1 31,339 pairs (30,285 different, 759 related, 167 narrower, 100 broader, 28 same);
the exporter needs only the hits (same, broader, narrower), about 300 for C1. Alignment rows for C1: paper 10 strict /
36 lenient, model 23 strict / 70 lenient.

## Proposed features

### Mode `gt`: ground truth only

The expert model has the same shape as Delve's output, so it reuses the existing pages, graph and tree through an
adapter that turns a GT view into the taxonomy structure the wiki builder reads:

- GT decision → dimension page; GT option → value page (options with no decision, `unattached` in the model view,
  go to a separate list, like the dropped page);
- forces, impacts and decision links → extra sections and graph edges that the LLM wiki does not have;
- each item cites its GT `source` (paper table and page, or code-model line) instead of quoted passages;
- no source pages, critic scores, core dimensions or contested values: these depend on corpus evidence the GT lacks.
  Hide those pages and filters rather than show them empty;
- one view per export (`--gt-view paper|model`); a `both` view would badge each item from the crosswalk;
- the index and overview say plainly that this is the expert reference, with the study and its provenance.

Cheap: mostly an adapter plus template conditions, about half a day.

### Mode `overlay`: run plus ground truth

1. **Expert reference pages.** A new sidebar shelf ("Expert reference") with one page per GT decision and option
   (and forces/impacts only where the view has them). Each page shows the GT `source` location and a badge from the
   crosswalk ("both views" / "model only").
2. **Cross-links both ways.**
   - Value page: matched expert options with label and the judge's reason.
   - Dimension page: aligned expert decision (strict / lenient, share).
   - Expert option page: the values that found it, or "missed".
3. **Comparison page** (synthesis), one section per expert decision: options found vs. missed (recall gaps); values
   with no match (new findings or noise); expert decisions no dimension aligns with. Includes the headline scores
   from `_gt_metrics.json`. Complements the existing Evaluation page (LLM critic scores only).
4. **Graph and tree views.**
   - GT decision and option nodes with a distinct shape; edges for matches (style by label).
   - Off by default: a "show ground truth" toggle and a paper/model switch, so the graph does not double in size
     (C1 model view adds about 214 nodes).
   - Tree: the existing edge tracing would then show which expert options a selected value covers.

**Cheapest useful slice:** items 2 and 3 only (no new graph nodes), about half a day. Full overlay: about 1–1.5 days.

Optional later: link a `gt` wiki and an `llm` wiki exported side by side (matched items point to each other), as an
alternative to the single overlay wiki.

### Suggested order

1. `gt` mode (adapter; also checks the GT loaders).
2. Overlay cross-links and comparison page.
3. Overlay graph and tree layer.

## Implementation sketch

- `benchmark/export_wiki.py`: new flags
  - `--mode llm|gt|overlay` (default `llm`, so current exports are unchanged). The `taxonomy` positional becomes
    optional in `gt` mode and required otherwise; fail with a clear message when a mode lacks its inputs
    (`gt`/`overlay` without `--gt`, `overlay` without matcher outputs);
  - output folder default: `<run>_wiki/` for `llm`, `<run>_overlay_wiki/` for `overlay`, `<case>_gt_<view>_wiki/` next to
    `--gt` (or `--out`) for `gt`;
  - `--gt <case>/gt` (folder with `gt_paper.json`, `gt_model.json`, `gt_crosswalk.csv`);
  - `--gt-match <run>_gt_match.json` and `--gt-alignment <run>_gt_alignment.csv` (default: siblings of the run named
    `<run-label>_<timestamp>_gt_*`; `--gt-metrics` likewise);
  - `--gt-view paper|model|both` (overlay default `both`, with a badge per item; `gt` mode default `model`).
  - Record the mode and the GT inputs in the export manifest (`raw/`).
- `src/taxonomy_generator/wiki/model.py`:
  - `Inputs.mode`; page builders skip what a mode does not have (sources, evaluation, core, contested in `gt`);
  - GT adapter for `gt` mode (GT view → dimensions and values the builder already renders);
  - loaders (`load_gt`, `load_gt_matches` keeping only hits, `load_gt_alignment`);
  - `Inputs` fields; `_assign_paths` for GT pages (e.g. `reference/decisions/…`, `reference/options/…`);
  - `gt_decision_page`, `gt_option_page`, `comparison_page`; cross-link sections in `dimension_page` and `value_page`;
  - GT nodes/edges in the graph and tree builders, tagged so the templates can filter them.
- `src/taxonomy_generator/wiki/render.py` and templates: nav shelf, graph/tree toggle and view switch, node shape.
- Tests next to the existing wiki tests: mode argument validation; `gt` mode pages for a small GT fixture (decisions,
  options, unattached options, no source or evaluation pages); loaders (hits only); overlay cross-links, missed
  options, view filtering; `llm` mode unchanged (regression).
- Docs: `USAGE.md` wiki section (flags and an example), `docs/DESIGN_SPACE_EXPLORATION.md` §13 pointer to this plan.

## Open questions and caveats

- **Labels are LLM judgments, not independent.** gpt-5.6-luna is both generator and matcher judge, and the labels are
  not yet validated against human gold (A6). Pages should say "matcher judgment" and show `label_source`.
- **The match file does not record the view.** Pairs carry `gt_id` only; resolve the view through the crosswalk (ids are
  shared across views). Verify that every `gt_id` in the pairs resolves in at least one view before building.
- **Many-to-many.** A value can match several options (e.g. broader); an option can be found by several values. A value
  can be a hit under one view's alignment and not the other's.
- **Which taxonomy view the matcher scored** (selected vs. final clusters): confirm in
  `src/taxonomy_generator/evaluation/gt_match.py` that `system_id`s refer to the same clusters the wiki shows
  (`--view selected` by default); otherwise show only matches whose value exists in the wiki.
- **Only runs scored with `--match-gt`.** C3 has no GT; new runs (main runs with seeds) must be scored first.
- **Sharing.** Model view: from an Apache-2.0 replication package. Paper view: derived from published papers (decision
  and option names, page references). C1/C2 wikis already stay local because they quote source texts; with GT, matches
  and scores they are private analysis wikis. Do not publish them on GitHub Pages.

## Re-export commands (current state, without GT)

```bash
PY=/Users/adiazpace/opt/anaconda3/envs/taxonomy/bin/python
$PY benchmark/export_wiki.py examples/c1-ml-workflow/u7/c1-u7b-tools_taxonomy_20261005_122709.json \
  --corpus examples/c1-ml-workflow/c1-ml-workflow_corpus.json --sources benchmark/c1-ml-workflow/sources.csv \
  --config examples/c1-ml-workflow/c1_ml_workflow_config.yaml --evaluation --core-min-sources 10
$PY benchmark/export_wiki.py examples/c2-rl-monitoring/u7/c2-u7b-tools-norelevance_taxonomy_20261005_110747.json \
  --corpus examples/c2-rl-monitoring/c2-rl-monitoring_corpus.json --sources benchmark/c2-rl-monitoring/sources.csv \
  --config examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml --evaluation --core-min-sources 10
```

Source summaries are read from `benchmark/<case>/source_summaries.json` (generated 2026-10-09 with gpt-5.6-luna;
not committed yet).

## Done when

- `--mode gt` exports the paper and model views of C1 and C2 as standalone expert wikis.
- `--mode overlay` exports C1 and C2 with expert pages, cross-links and the comparison page; missed options and
  unmatched values are listed, and the numbers agree with `_gt_metrics.json`.
- `--mode llm` (and no `--mode`) is byte-identical to today's export (except the exporter version).
- Tests pass; `USAGE.md` documents the flags.
