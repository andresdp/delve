---
title: "feat: wiki graph view with a radial layout and a domain node"
type: feat
status: proposed (2026-10-31)
date: 2026-10-31
related: >-
  src/taxonomy_generator/wiki/{model,render}.py, src/taxonomy_generator/wiki/templates/{graph,tree}.html.j2,
  src/delvedspace/{wiki_build,workspace}.py, src/delvedspace/templates/ddspace.yaml,
  docs/plans/improvements.md
---

# Radial layout and a domain node in the wiki views

## Goal

1. The graph view (`graph.html`) can switch between today's force layout and a **radial layout**: concentric
   rings that move outwards from the domain, through the dimensions, to the values and then to sources, systems
   and design points.
2. An artificial **domain node** (for example *git-at-scale*) sits at the centre of the graph, linked to every
   dimension. The tree view (`tree.html`) shows the same node as its root.
3. The domain's label is the workspace name by default. The user can change it with `taxonomy.domain`, in `ddspace.yaml` or the pipeline's `config.yaml`.

## Current state (2026-10-31)

- **Graph view.** A d3 force simulation ([graph.html.j2:294](../../src/taxonomy_generator/wiki/templates/graph.html.j2)).
  - Node kinds: `dimension`, `value`, `source`, `system` and `design`.
  - It already has filters (status, k, relation types), a "Re-lay out without relations" toggle and "Fit to
    view".
  - It has no central node.
- **Graph data.** The data is the wiki's graph export, inlined in `graph.html` and written to `raw/graph.json`
  (`WikiModel.graph_data`, [model.py:1010](../../src/taxonomy_generator/wiki/model.py)). `ddspace query` and
  agents read `raw/graph.json`, so a new node kind there would change `query info` counts and query output.
- **Tree view.** It already has a root node (`kind: "root"`), labelled `taxonomy_name` and linked to `index`
  ([model.py:1006](../../src/taxonomy_generator/wiki/model.py)). `taxonomy_name` comes from
  `taxonomy.name` in `ddspace.yaml`, then the run file, then the folder name
  ([wiki_build.py:377](../../src/delvedspace/wiki_build.py)).
- **Workspace name.** `ddspace init` writes the name into `taxonomy.name`. The `wiki:` block holds the wiki's
  answers: `quotes`, `source_summaries`, `design_points`, `core_min_sources`, `stale_after` and `html_report`.

## Design

### KTD1. The domain node lives in the views, not in `raw/graph.json`'s nodes

- The graph export gains one identity field, `domain` (a string), next to the existing `name` and `run`.
- `graph.html` and `tree.html` create the domain node in the browser from that field.
- `raw/graph.json` keeps the same nodes and edges. `ddspace query` output and its counts do not change, and
  `GRAPH_SCHEMA_VERSION` stays 1 (an added identity field is backwards compatible).

### KTD2. Label: `taxonomy.domain`, falling back to the name

This applies to the approach and the tool alike (see `improvements.md`).

- The label goes into the shared configuration schema, next to `taxonomy.name`, so `config.yaml` and
  `ddspace.yaml` both accept it: `taxonomy.domain: null`, commented "Label of the central node in the wiki's
  graph and tree views (null = `name`)".
  - The `wiki:` block exists only in `ddspace.yaml`, so it would not reach the pipeline.
- `null` resolves to the same name the tree's root uses today (`taxonomy.name`, then the run file's
  `taxonomy_name`, then the folder name). In a workspace, `taxonomy.name` is the workspace name.
- Older configs and workspaces have no key and read it as `null`. `ddspace init` writes it from the template.
- The pipeline's wiki export (`benchmark/export_wiki.py`) and `ddspace wiki build` pass the resolved label to
  the same wiki code, so both get the domain node and the radial layout.

### KTD3. Radial layout: one ring per kind, positions from d3's radial force

- Add a "Layout: force | radial" control next to "Fit to view". The choice is remembered per viewer in
  `localStorage`, wrapped in try/catch like the theme.
- **Rings by kind:**

  | Ring | Kind |
  |---|---|
  | 0 | domain |
  | 1 | dimensions |
  | 2 | values |
  | 3 | sources and systems |
  | 4 | design points |

  - Hidden kinds collapse, so the rings close up.
  - Ring radii scale with the viewport and the number of nodes on the ring.
- **Simulation:** `d3.forceRadial(r(kind), cx, cy)` with a strong strength, plus the existing link, collide and
  charge forces at lower strength. Each value then settles near its dimension's angle.
- **Ordering:** dimensions are spaced evenly around ring 1, in the order of the dimension list (core first).
  Each dimension's values get an angular sector centred on it, so a dimension's values do not interleave with
  another's.
- **Domain edges:** domain–dimension links are drawn as thin spokes. They join the force layout too, with a
  neutral style.
- **Relations between dimensions:** these become chords across ring 1. The relation-type filters and the
  "without relations" toggle keep working.
- **Switching layouts** keeps the selection, the filters and `#node=` deep links.

### KTD4. The tree view uses the same label

The root node's label becomes the resolved domain. It keeps `kind: "root"` and its link to `index`. Nothing else
in the tree changes.

## Implementation units

| Unit | What | Files |
|---|---|---|
| R1 | `taxonomy.domain` in the configuration schema, `config.yaml` and the `ddspace.yaml` template; resolve the label in `wiki_build` and `export_wiki`; `Inputs.domain`; `domain` in the graph export's identity; the tree root uses it | `settings.py`, `configuration.py`, `config.yaml`, `templates/ddspace.yaml`, `wiki_build.py`, `benchmark/export_wiki.py`, `wiki/model.py` |
| R2 | Domain node and spokes in `graph.html` (force layout first) | `graph.html.j2` |
| R3 | Radial layout control, ring radii, angular sectors, remembered choice | `graph.html.j2`, `style.css` |
| R4 | Docs: `USAGE.md` (wiki settings), `SETTINGS.md`, the wiki's "How to read" text | docs |

## Verification

- **Unit tests:**
  - the domain resolves to `taxonomy.name` when `taxonomy.domain` is null or missing, and to the yaml value when
    set;
  - the export carries `domain`;
  - `raw/graph.json` nodes and edges are unchanged against a fixture;
  - the tree root carries the label.
- **Browser check** on the C1 mined wiki (32 dimensions, 279 values) and the C1 expert wiki:
  - both layouts render;
  - filters and the relations toggle work in both;
  - `#node=` deep links work;
  - nothing scrolls horizontally on a phone-width window.
- **Performance:** the C1 mined graph has about 1,000 nodes with sources shown. The radial layout must settle in
  under 2 seconds. If it doesn't, hide sources by default in radial mode.

## Risks

| Risk | Mitigation |
|---|---|
| Value rings get crowded (about 280 values) | Angular sectors per dimension; labels only on hover or zoom for ring 2+, as today |
| A view-only node confuses readers who also read `raw/graph.json` | Document that the domain node exists only in the views |
| Forces (2a plan) add another kind | Leave room for a ring for forces, hidden by default; decided in that plan |

## Open questions

1. Should the radial layout become the default when the space has more than N dimensions?
2. Should the index page show the domain label as its title (today it shows `taxonomy_name`)?
