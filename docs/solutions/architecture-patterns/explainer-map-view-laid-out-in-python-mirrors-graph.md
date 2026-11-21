---
title: The explainer's map view is laid out in Python and mirrors the graph's selection
date: 2026-11-21
category: architecture-patterns
module: wiki
problem_type: architecture_pattern
component: frontend
severity: medium
applies_when:
  - "Adding a second picture of a rationale run (or of any explainer data) beside the radial graph"
  - "Drawing a fixed-grid diagram whose layout can be decided before the page loads"
  - "Wiring a new view into the explainer's selection, tabs and details pane"
  - "Deciding whether a view applies to zero-shot rationale files as well as space-backed ones"
tags: [explainer, map-view, inline-svg, rationale, search, explain, selection-state, zero-shot]
---

# The explainer's map view is laid out in Python and mirrors the graph's selection

## Context

The explainer showed a run through tabs (decisions, comparison, trajectory) and a radial graph. None showed
the run's shape and trade-offs at a glance: the search lanes had no trade-offs or changes, and explain had no
overview at all. Hand-drawn figures of the toy runs for the Designing 2027 paper did, so the same diagram was
added to the explainer as an experimental **map view**, behind a Graph | Map switch in the graph pane
(PR #20).

## Guidance

**1. Compute the layout in Python; let the template only draw it.** `_map()` in
`src/taxonomy_generator/wiki/explainer.py` builds the grid from `_search_grid()` (approaches as columns,
rounds as rows) or `_explain_grid()` (the solution above its regions, each region above its contrasts). It
returns every box's position, text lines, style classes and tooltip, every arrow's SVG path, and the page
size. `src/taxonomy_generator/wiki/templates/explainer-map.html.j2` draws that as inline SVG, and the
explainer page imports it as macros.

- The diagram is deterministic, so unit tests assert rows, columns, change lines, trade-offs, forced/free
  marks and arrow kinds directly on `page_data()` (`tests/unit_tests/test_rationale_build.py`), with no
  browser needed.
- The page shows the diagram without JavaScript; only selection and the switch need the script.
- Contrast this with the lanes and the questions-options-criteria links, which are drawn in the browser from
  HTML positions (`drawLanes`, `overlay`), because their layout depends on how HTML wraps.

**2. Mirror the graph's selection; keep no second selection state.** Map boxes join the existing step-click
selector, so a click calls the same `selectStep()` as a click on a design point in the graph. `applyView()`
already computes the set of points the graph lights (`shownPoint()`), and it now also toggles a `lit` class
on each map box whose point is in that set. The map therefore follows every tab: a selected step, an
alternative or option on the Decisions tab, or the comparison. Tab switches still clear the selection, as
`docs/solutions/ui-bugs/graph-filter-change-kept-stale-selection-fade.md` requires.

**3. Switch views with `visibility`, not by removing the graph.** The switch hides the radial graph with
`visibility: hidden` and lays the map over it. The graph keeps its size and layout, so switching back needs
no re-layout, and the selection survives the switch.

**4. Shorten ids for the boxes and explain them in a legend.**
- Boxes show value ids (`4.2 → 4.3`), never labels, so lines fit a fixed width.
- A line too long is cut with an ellipsis. When a step changes several values, the box shows one pair and
  `+N more`: the pair is cut, never the count.
- A legend under the map names every dimension and value id the map uses.
- Tooltips carry only what the box does not show: an alternative's design point, then what the box's
  trade-off means.

**5. Gate on the label graph, not on a space.**
- A zero-shot rationale file gets a label graph with made-up ids (`z:1`, `z:1.2`), so `_Space.with_space` is
  true for it.
- The map uses `with_space`, so zero-shot explainers get it too, and `_short()` reads `z:` ids like a space's
  (`z:1.2` → `1.2`, `z:1` → `d1`).
- `space.wiki` is the flag that means "a design space is behind this file". A review caught the first version
  gating the map on `with_space` while the plan meant "space-backed only". Choose the flag that matches the
  intent.

## Why This Matters

- **Testable.** Layout bugs found in review were all fixable and testable in Python: a count cut off, marks
  for changes the box did not show, arrows through stacked boxes, and wrong same-column arrows. A
  browser-drawn layout would have needed a browser test for each.
- **One selection.** A second selection state in the map would drift from the graph's: the stale-selection
  class of bug the earlier ui-bugs learning documents.
- **The right gate.** `with_space` and `wiki` look alike, and the wrong one silently shows or hides a view for
  a whole class of files.

## When to Apply

- Adding any further view of a run to the explainer: lay it out in Python when its geometry is a grid; draw
  it in the browser only when it depends on HTML text flow.
- Making any element selectable: reuse `selectStep()` and the lit set rather than tracking selection in the
  new view.
- Gating a feature on "has a space": use `space.wiki`. Use `with_space` when zero-shot files qualify too.

## Examples

- A selected alternative on the Decisions tab lights its box on the map. No map code handles the Decisions
  tab; the map only reads the lit set:

  ```javascript
  // in applyView(), after the graph's own updates
  document.querySelectorAll(".map-node").forEach((el) =>
    el.classList.toggle("lit", lit.has(pid(Number(el.dataset.step)))));
  ```

- Contrast boxes in explain are read against the solution, so a contrast that adds a dimension its region
  lacks still names the solution value it tests. `_map()` reuses `_diff(contrast_point, solution_point)` and
  keeps only entries where both sides are set.
