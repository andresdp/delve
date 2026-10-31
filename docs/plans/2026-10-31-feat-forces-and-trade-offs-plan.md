---
title: "feat: forces and trade-offs in the design space (2a: represent, import, show)"
type: feat
status: proposed (2026-10-31); scope 2a only, mining forces (2b) and evaluating them (2c) deferred
date: 2026-10-31
related: >-
  src/delvedspace/{importer,point,query_cli,check}.py, src/taxonomy_generator/wiki/{model,query,okf}.py,
  src/taxonomy_generator/wiki/templates/{graph,tree}.html.j2, benchmark/gt_format.py,
  benchmark/c1-ml-workflow/gt/gt_model.json, benchmark/c2-rl-monitoring/gt/gt_model.json,
  study/cain2027/{build_workspaces,reference,score}.py,
  docs/plans/2026-10-15-refactor-taxonomy-data-layer-plan.md, docs/plans/improvements.md
---

# Forces and trade-offs (2a)

## Goal

Extend the design-space representation with the elements of the C1 and C2 expert models that it lacks today:

- **forces**: the quality attributes and concerns a decision must balance;
- **impacts**: how an option affects a force, rated `++`, `+`, `o`, `-`, `--` or `+/-`;
- **forces per decision**;
- **typed links between options**, such as is-a, can use, requires and rules out.

The C1 and C2 references come from grounded-theory studies (Straussian coding) of practitioner sources,
recorded as architectural design decision models. Forces correspond to the conditions and consequences of
axial coding's conditional matrix.

**Scope 2a:** represent these elements, keep them on `ddspace import`, and show them in the wiki, in `ddspace
query` and in `ddspace point`, so that a person or a coding agent sees the trade-offs of a combination of
values.

**Out of scope:** mining forces from sources (2b) and evaluating mined forces against the expert models (2c).
Mined spaces have no forces after this plan; every view must degrade to "nothing shown", never to an empty
section.

## Current state (2026-10-31)

### The expert models

Format: `benchmark/gt_format.py`.

| | C1 (ML workflow) | C2 (RL monitoring) |
|---|---|---|
| Decisions / options | 28 / 186 | 7 / 63 |
| Forces | 104 (no descriptions) | 43 |
| Decision–force links | 0 | 72 |
| Impacts | 737: `+` 258, `o` 157, `-` 125, `++` 119, `--` 74, `+/-` 4 | 150: `+` 130, `-` 20 |
| Decision links | 40, all "Consider If Not Decided Yet" | 6, eight distinct stereotypes (Enables, Constrains, Mandatory Next, ...) |
| Option links | 184, 15 stereotypes (Can Use 74, Consider If Not Decided Yet 22, Enables 21, Can Include 15, Is-a 12, ...) | none |

### The importer

`ddspace import --kind decision-model`, in `importer.model_to_taxonomy`:

- decisions become dimensions and options become values (`external_id` keeps the expert id);
- an option attached to several decisions becomes one value per decision, and unattached options are skipped;
- decision links become `affects` relations, with the stereotype as rationale.

Forces, impacts, decision–force links and option links are dropped.

### The mined representation

- Dimensions have values (status, stances, evidence) and relations to other dimensions (`requires`, `affects`,
  `constrains`, `co_occurs_with`, `refines`).
- Values have no relations to other values.
- The evaluation prompts state that the format has no forces
  ([metrics.py:15](../../src/taxonomy_generator/evaluation/metrics.py)).

### The CAIN study

- It holds forces out on purpose: condition E imports the model without them
  ([build_workspaces.py:128](../../study/cain2027/build_workspaces.py)).
- Scoring uses the hidden forces: relevant decisions come from summed impacts on the brief's forces
  (`reference.py`), and driver recall checks named forces (`score.py`).
- Showing forces to the agent would leak the scoring key.

## Design

### KTD1. Where the elements live (run file, KTD2 of the data-layer plan: extra keys survive)

| Element | Location | Shape |
|---|---|---|
| Forces | top-level `forces` | `[{id, name, description, external_id}]` |
| Impacts | on the value: `value["impacts"]` | `[{force_id, impact}]`, `impact` in `++ + o - -- +/-` |
| Forces per decision | on the dimension: `dim["forces"]` | `[force_id]` (C2's decision–force links; for C1, derived as the forces any of its values affects, marked `derived: true`) |
| Option links | on the value: `value["links"]` | `[{target_id, type, stereotype, label}]` |
| Decision-link stereotypes | on the relation: `relation["stereotype"]` | the original stereotype (today only in `rationale`) |

- **Why impacts live on the value:** they move with the value through relabels and moves. A merge combines the
  impacts, and a disagreement on one force becomes `+/-`.
- **Duplicate values:** when an option has become several values, each copy carries the option's impacts.

### KTD2. A small link vocabulary, with the original stereotype kept

Option-link stereotypes are mapped to a few types that the views and `point` can use:

| Type | Stereotypes |
|---|---|
| `refines` | Is-a, Has Variant, Extension |
| `uses` | Can Use, Uses, Includes, Can Include, Realizes, Can be Realized By |
| `requires` | Requires |
| `excludes` | Rules Out, Alternative To |
| `combines_with` | Can Be Combined With |
| `enables` | Enables |
| `considers` | Consider If Not Decided Yet |

- An unknown stereotype maps to `related`.
- The original stereotype is always kept in `stereotype`, so nothing is lost and the mapping can change later.

### KTD3. Import keeps forces by default; the study pins them off

- `ddspace import --kind decision-model` imports forces, impacts and links. `--no-forces` gives today's
  behaviour.
- `study/cain2027/build_workspaces.py` passes `--no-forces` explicitly.
- A test asserts that the E workspace contains no forces, impacts or force pages, so the study's scoring key can
  never leak into a rerun.

### KTD4. Trade-offs in `ddspace point`, with no LLM

For a design point, the trade-off summary gives, per force:

- each chosen value's impact;
- a summed score on the same scale as the study's `reference.py`: `++` = 2, `+` = 1, `o` = 0, `-` = -1, `--` =
  -2, and `+/-` = 0 but flagged as mixed;
- whether the combination helps, hurts or is mixed.

Options:

- `--forces f1,f2` restricts and orders the summary to forces the caller cares about (a brief's drivers).
- `excludes` and `requires` links between chosen values become warnings, next to today's warnings. This is the
  value-level consistency check that `DESIGN_SPACE_ROADMAP.md` Phase 4 deferred for lack of value-level
  relations.

The scale is defined in the library (`taxonomy_generator`). The study keeps its own copy, so its published
numbers never depend on library changes.

### KTD5. Graph schema version 2, read compatibly

- `raw/graph.json` gains node kind `force`, edges `impact` (value to force, with `impact`), `link` (value to
  value) and `concerns` (dimension to force).
- `GRAPH_SCHEMA_VERSION` becomes 2.
- `ddspace query` reads versions 1 and 2. On version 1, force subcommands say "this design space has no forces".
- `query info` reports forces and impacts only when there are any.

### KTD6. Depends softly on the data layer

- **Preferred order:** after data-layer U1 (model and lossless conversion). Then `Force`, `Impact` and
  `ValueLink` are model classes with validation:
  - an impact must name an existing force;
  - the symbol must be on the scale;
  - a link target must be an existing value;
  - a dimension's forces must exist.
- **If 2a comes first:** the same checks go into `importer` and `ddspace check`, and move into the model later.

### KTD7. The approach and the tool alike

Forces are not only an import feature of `ddspace`. On the pipeline side:

- **Seeded runs keep them.** A seed taxonomy (`--taxonomy`, `load_seed_taxonomy`, `ddspace update`) brings its
  top-level `forces` and the values' `impacts` and `links` into the run. The pipeline writes them back to the run
  file.
- **The editor preserves them.** `move_value` and `relabel_value` keep impacts and links. `merge_values`
  combines impacts (KTD1). `remove_value` drops links that point at the removed value.
- **Outputs show them.** The pipeline's HTML report and wiki export show forces as `ddspace wiki build` does.
- **The ground-truth converter round-trips.** `evaluation_report.taxonomy_to_gt` exports forces, impacts and
  links, so `taxonomy_to_gt(model_to_taxonomy(m))` keeps them.

Mining does not create forces (2b), but it must not lose the ones a seed brings.

## Implementation units

| Unit | What | Files |
|---|---|---|
| F1 | Elements and validation (model classes after U1, else importer and `check`) | `model/` or `importer.py`, `check.py` |
| F2 | Importer: forces, impacts, decision–force links (or derived), option links with the vocabulary, decision-link stereotypes; `--no-forces`; the study pins it | `importer.py`, `cli.py`, `study/cain2027/build_workspaces.py` |
| F3 | Wiki pages and views (below) | `wiki/model.py`, `wiki/render.py`, templates |
| F4 | `ddspace query forces [--dimension D]`, `query impacts REF` (a value or a force), forces and links in `query show`; graph schema 2 | `wiki/query.py`, `query_cli.py` |
| F5 | Trade-offs and link warnings in `ddspace point` (KTD4); the point description prompt receives the trade-offs | `wiki/query.py`, `point.py`, `wiki/llm_texts.py` |
| F6 | Agent guide (`AGENTS.md` template): how to read trade-offs. OKF export: forces and impacts | `agent.py`, `wiki/okf.py` |
| F6b | Pipeline side (KTD7): seeds carry forces; editor operations preserve impacts and links; report and wiki export; `taxonomy_to_gt` exports them | `utils.py`, `taxonomy_editor.py`, `html_report.py`, `benchmark/evaluation_report.py` |
| F7 | Docs and tests: `USAGE.md` (new query subcommands; the USAGE test enforces it), `CONCEPTS.md` ("Force", "Impact", "Option link"), `SETTINGS.md` | docs, tests |

### F3, the wiki, in more detail

- **A force page per force:**
  - name and description;
  - the values it affects, grouped from `++` to `--`;
  - the decisions it concerns.
- **Each dimension page:**
  - a "Trade-offs" table (values × the dimension's forces, cells `++` to `--`, empty cells for no rating);
  - its option links.
- **Each value page:** its impacts and its links.
- **Graph view:**
  - force nodes are hidden by default, with a "Show forces" toggle (C1 has 737 impact edges);
  - in the radial layout (radial-layout plan), forces take an outer ring.
- **Tree view:** a "Forces" branch under the domain node.
- **Mined spaces** have no forces: none of these sections or toggles appear.

## Verification

- **Counts:** importing C1 and C2 keeps every force, impact and link. The wiki counts must equal the model's
  counts, minus the impacts on unattached options, which are reported.
- **Round trip:** the run file loads, saves and reloads unchanged (data-layer KTD2).
- **No change elsewhere:**
  - the CAIN E workspace is identical to today's, apart from build timestamps, because of `--no-forces`;
  - mined workspaces and their wikis are unchanged, apart from `schema_version`.
- **`point`:** on the C1 model, the summed scores for the study's briefs equal `reference.py`'s ranking (same
  scale), checked by test.
- **Browser check:** a force page, a dimension trade-off table, and the forces toggle in both graph layouts.

## Risks

| Risk | Mitigation |
|---|---|
| Leaking the study's scoring key into the E condition | KTD3: explicit `--no-forces` in the study plus a guard test |
| Clutter: 737 impacts in the graph | Hidden by default; tables on pages, not edges, as the main view |
| Agents over-trusting expert ratings as facts | The pages and `point` say where ratings come from (the expert model, with its source line) |
| The link vocabulary is lossy | The original stereotype is always kept (KTD2) |
| Older wikis break `ddspace query` | Version 1 and 2 are both read (KTD5) |

## Later (2b, 2c; not planned here)

- **2b:** mine forces and impacts from sources, with evidence and stances. Candidates: an axial-coding step for
  conditions and consequences, or the quality attributes named in the use case.
- **2c:** evaluate mined forces and impacts against C1 and C2 (force matching and impact agreement), reusing the
  independent matcher.

## Open questions

1. Should C1's decision–force links be derived from impacts (KTD1) or left empty?
2. Should `point` without `--forces` show every force, or only those where the chosen values differ from the
   alternatives?
