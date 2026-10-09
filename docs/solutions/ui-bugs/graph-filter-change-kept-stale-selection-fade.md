---
title: Wiki graph filter seemed to show one dimension because a stale selection kept the rest faded
date: 2026-10-08
category: ui-bugs
module: wiki
problem_type: ui_bug
component: frontend
symptoms:
  - "Turning on the graph view's core-dimensions-only filter appeared to show a single dimension (Authority Synchronization) instead of the 18 core dimensions"
  - "The other core dimensions were drawn but faded, because a node selected earlier kept highlighting only its neighborhood"
  - "The export data and the filter predicate were correct (C3 run: 18 of 22 dimensions core), so a working filter looked broken"
root_cause: logic_error
resolution_type: code_fix
severity: medium
tags: [design-space-wiki, d3-force-graph, graph-filters, node-selection, stale-ui-state, url-hash, core-dimensions]
---

# Wiki graph filter seemed to show one dimension because a stale selection kept the rest faded

> This fix is on branch `feat/design-space-wiki` (commit `f652098`, "fix(wiki): graph filters clear the current selection"). As of 2026-10-08 the branch is not merged into `main` and has not been pushed. Line numbers refer to `src/taxonomy_generator/wiki/templates/graph.html.j2` at `63869b1`.

## Problem

The design-space wiki's graph view is a d3 v7 force graph. `benchmark/export_wiki.py` writes it offline, with the data inlined as JSON. The user turned on the "★ core dimensions only" filter and asked whether it was correct, because only "Authority Synchronization" seemed to remain. Neither the data nor the filter was at fault. In the C3 run, 18 of 22 dimensions are core (the rule: ≥ 2 sources, or, when a system map is given, ≥ 2 systems). The `visible()` predicate (lines 182-188, core check at line 184) hides the non-core dimensions and their values, and nothing else. The view looked wrong because a node selection from earlier was still active.

## Symptoms

- With the core-only filter on, almost every node and edge was faded. Only one dimension and its neighborhood were drawn at full opacity, so the filter seemed to have returned one dimension.
- The selection is saved in the URL (`#node=...`) and restored on load, so a reload brings the same faded state back.

## What Didn't Work

- **Suspecting the export data or the core rule.** The exported graph JSON contained 18 core dimensions.
- **Suspecting the filter predicate.** `visible()` keeps the right nodes. The problem was in how the visible nodes were drawn (faded or not), not in which nodes were visible.

## Solution

Before the fix, every filter control called `render()` directly:

```js
document.querySelectorAll("#controls input[type=checkbox], #kfilter").forEach((el) => el.addEventListener("change", render));
```

Now a filter change drops the selection and its `#node=` hash, then lets the view re-fit (lines 326-332):

```js
// A filter change shows the filter's full result: drop any selection (and its #node= link) and re-fit.
document.querySelectorAll("#controls input[type=checkbox], #kfilter").forEach((el) => el.addEventListener("change", () => {
  if (selected) clearSelection();
  if (location.hash) history.replaceState(null, "", location.pathname + location.search);
  userMoved = false;
  render();
}));
```

`clearSelection()` (lines 286-293) does the following:
- sets `selected = null`;
- removes `dim-out` from every node and edge;
- resets the strokes and labels;
- resets the info panel.

## Why This Works

These are the parts of the code that kept the old highlight in place:
- **`select()`** (lines 296-324) sets `selected` and calls `highlight(id)`. It also writes `#node=<id>` into the URL (line 323), and the page reselects that node on load (lines 354-355).
- **`highlight()`** (lines 278-285) adds the `dim-out` class to everything outside `neighborhood(id)`.
- **`neighborhood()`** (lines 264-277) covers the selection, its neighbors, and the elements linked to those neighbors, counting only nodes that are shown. A neighboring dimension is expanded only when the selection is one of its values.
- **`render()`** keeps a selection whose node is still visible and highlights it again (line 251). It also skips the automatic fit while anything is selected (`if (!userMoved && !selected) fit(0)`, line 249).

So before the fix, a filter change recomputed which nodes were visible but then faded nearly all of them again, and left the camera where it was.

Clearing the selection, the hash and `userMoved` removes all three effects:
- Line 251 no longer highlights the old selection again.
- A reload has no hash to restore.
- `fit(0)` frames the whole filtered set.

## Prevention

- **General rule.** When a change alters which items are visible, reset or re-check the state built on the previous visible set. That state includes selection, highlight or fade, focus, zoom, and anything saved in the URL hash or query string. If a highlight should deliberately survive a filter change, the UI should show that it is still active.
- **New filter controls go through the same handler.** Wire any new filter control into the "filter changed" handler (lines 326-332), not straight to `render()`.
- **Manual check.**
  1. Click a dimension and confirm that the URL now has `#node=`.
  2. Toggle each filter: kind, status, design-point group, k, and core only.
  3. After each toggle, confirm that nothing stays faded, the hash is gone, and the view re-fits.
  4. Reload the page and confirm that no selection comes back.
- **Optional automated check.** A headless-browser test (e.g. Playwright) on an exported `graph.html` would cover this. After clicking a node and then toggling `#core-only`, the test should assert:
  - `document.querySelectorAll("g.node.dim-out").length === 0`;
  - `location.hash === ""`;
  - the number of visible dimension nodes equals the number of core dimensions in the inlined JSON.

## Related Issues

- [narrative-summary-includes-unscoped-explanation-text.md](../logic-errors/narrative-summary-includes-unscoped-explanation-text.md) covers a related case in another part of the system: a filtered view showed content from outside the filter's scope. The common rule is that everything feeding a filtered view must be re-scoped when the filter changes.
