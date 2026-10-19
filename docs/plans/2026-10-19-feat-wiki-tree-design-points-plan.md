---
title: "feat: design points and systems in the wiki tree view"
type: feat
status: planned
date: 2026-10-19
---

# feat: design points and systems in the wiki tree view

## Goal

Extend the wiki's tree view (`html/tree.html`) so that, besides decision points → values (→ sources), it can show
**design points** and **systems** as further columns to the right, linked to the values they combine or take. The
tree keeps expanding from left to right; the new columns are optional and turn on only when the wiki has design
points or systems.

A hand-built prototype on a 17-node slice of C3 (3 decision points, 8 values, 3 design points, 3 systems) showed the
view works: values grouped under their decision point, each design point placed level with the values it combines,
each system linked to its design point, the relations between decision points drawn as arcs on the left, hover
tracing a whole chain, and a details panel on click. This plan turns it into a general renderer feature.

## Current state

- `src/taxonomy_generator/wiki/templates/tree.html.j2`: a d3 tree (`d3.tree().nodeSize`) of root → dimensions →
  values → sources, with collapse/expand, search, status, core and source filters, hover tracing, and columns that
  start after the widest label of the previous level. No details panel (labels link to pages).
- `wiki/model.py` `tree_data()`: the nested tree (dimensions → values → sources). It has **no design points or
  systems**. `raw/tree.json` is this tree; `ddspace query` and agent guides read it.
- `wiki/model.py` graph: design-point nodes (`kind: design`, `group`, `k`, `tag` = system code, `design` edges to
  values) and system nodes (`kind: system`, `system` edges to values with a weight). Present only when the run has a
  design-point file and a passage-to-system map.
- `wiki/render.py` renders `tree.html` with the tree data only; `graph.html` already gets `has_designs` /
  `has_systems`.
- Size of a real wiki: the published C3 sample has 8 dimensions, 89 values, 24 design points (k = 2 and 3), 6 systems
  and 73 system → value edges; full study runs reach about 45 dimensions and 300 values.

## Requirements

- R1. When the wiki has design points, the tree view can show a **Design points** column; when it has systems, a
  **Systems** column. Each is a toggle in the toolbar, off by default above a size threshold (see R6).
- R2. A design point is linked to each value it combines and placed level with them (mean row), without overlapping
  its neighbours.
- R3. A system is linked to its attested design points. Hovering a system also highlights every value it takes (its
  `system` edges), without drawing those edges permanently.
- R4. Collapsing a decision point keeps its design-point links, attached to the decision point's row instead of its
  hidden values.
- R5. Relations between decision points can be shown as arcs left of the decision-point column, with the same
  per-type dash styles as the graph view; a toggle hides them.
- R6. Readability at real size: design-point links are drawn only for expanded decision points, or on hover when more
  than a set number of design points would be drawn (initially 30 links); design points and systems are ordered by
  the mean row of what they link to, to reduce crossings.
- R7. Existing behaviour stays: search, status / core / source filters, expand / collapse all, hover tracing, page
  links. Sources stay a column after values; when design points are shown, sources default to off.
- R8. A details panel (right side), as in the graph view: kind, label, description, the decision point of a value,
  the system of a design point, and the open-page link. Clicking a label still opens its page (or the panel opens on
  click on the symbol; to settle in U3).
- R9. No change to the OKF Markdown bundle, `raw/tree.json`'s existing fields, queries or agent guides. No LLM calls.

## Key technical decisions

- KTD1. **Data:** extend the tree export with two optional top-level lists instead of nesting: `designs`
  (`id`, `label`, `k`, `group`, `description`, `values`: value ids, `system`: system id or null, `href`) and
  `systems` (`id`, `label`, `description`, `href`). Taken from the graph's design and system nodes and edges, so the
  two views cannot disagree. Existing fields of `tree.json` are unchanged, so readers of it are not affected.
- KTD2. **Layout:** replace `d3.tree()` with an explicit row/column layout. Rows: one per shown value (or per
  collapsed decision point), grouped by decision point; sources as indented rows under their value, as today.
  Columns: decision points, values, [sources], design points, systems, each starting after the widest label (and its
  heading) of the column before. Design points: y = mean of their linked rows, then pushed apart to a minimum gap
  in order; systems: y = mean of their design points, pushed apart the same way.
- KTD3. **Edges:** tree edges (decision point → value → source) as today (`d3.linkHorizontal`); design edges from a
  common line right of the value column; system edges from the end of the design point's label. Relation arcs: cubic
  curves left of the decision-point column with an arrow marker.
- KTD4. **Systems link through design points** (R3), not through their 70+ value edges; the value edges appear only
  as hover highlights.
- KTD5. **One template**, `tree.html.j2`, with the new columns behind `has_designs` / `has_systems`, rather than a
  second page; the header's view buttons stay as they are.

## Implementation units

- **U1. Data.** `model.py`: add `designs` and `systems` to the tree export from the graph data; `render.py`: map their
  `href`s like the tree's, pass `has_designs` / `has_systems` to `tree.html.j2`. Tests in
  `tests/unit_tests/test_wiki_export.py`: the lists appear when the run has design points / a system map, are absent
  otherwise, and reference only value ids present in the tree; the existing tree fields are unchanged.
- **U2. Layout engine.** In the template: the row/column layout (KTD2), collapse handling (R4), headings, widths from
  labels and headings, ordering by mean row (R6).
- **U3. Edges, tracing, panel.** Design / system / relation edges (KTD3); hover tracing of a design point (its values,
  system) and of a system (its design points, values); the details panel (R8).
- **U4. Toolbar and thresholds.** Toggles for design points, systems, relations, sources; the link threshold of R6;
  search and filters applied to the new columns (a filtered-out value drops its design-point links).
- **U5. Verification and docs.** Build the C3 sample wiki and one full study wiki, check them in a browser (light and
  dark), check the timing on the largest wiki, update `USAGE.md` (tree view section) and the wiki's own help text.

## Test scenarios

- A wiki without design points or systems renders the tree exactly as before (no new columns, no toggles).
- C3 sample: 24 design points and 6 systems render; every design point is level with its values' mean row within the
  minimum gap; hovering a system highlights its values.
- Collapsing a decision point keeps its design points linked to its row.
- Filtering out a status hides values and drops the design-point links to them; a design point with no remaining
  links is hidden.
- Search for a design-point or system label finds and reveals it.

## Effort and order

About 2–3 days: U1 half a day; U2 and U3 a day to a day and a half; U4 half a day; U5 half a day. A reduced first
version (U1, U2, U3 without the panel, links on hover only) takes about a day, if a screenshot is needed earlier.

## Out of scope

- The graph view, the OKF bundle, `ddspace query`, agent guides.
- Editing design points or systems from the wiki.
- New design-point sampling or system maps (the view shows what the run already has).

## Risks

| Risk | Mitigation |
|---|---|
| Too many crossing links on large wikis | Ordering by mean row, links on hover above the threshold, toggles off by default |
| Labels too long for one column (full value names) | Truncate with the full label in the tooltip and panel, as the graph view does |
| `tree.json` readers break | Only new top-level fields; a test pins the existing shape |
