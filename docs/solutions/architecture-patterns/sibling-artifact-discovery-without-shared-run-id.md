---
title: Sibling-Artifact Discovery Without a Shared Run ID
date: 2026-09-03
category: architecture-patterns
module: taxonomy_generator
problem_type: architecture_pattern
component: service_layer
severity: medium
applies_when:
  - "Composing one artifact from several files that were written independently, at different times, by different code paths, with no run ID linking them"
  - "Matching a saved taxonomy JSON to whichever sibling report/biplot/evaluation/documents files belong to the same run"
  - "Writing a resolver that must degrade gracefully (never raise) when a sibling is missing or its match is ambiguous"
tags: [sibling-artifacts, html-report, artifact-matching, fail-soft, filename-timestamp, taxonomy-generator]
---

# Sibling-Artifact Discovery Without a Shared Run ID

## Context

The `--html-report` CLI mode (`src/taxonomy_generator/html_report.py`) composes one self-contained HTML page from a taxonomy JSON plus up to four sibling artifacts: a grounded-theory report `.md`, a PCA biplot `.html`, an evaluation scoreboard `.json`, and a documents `.json`. These are written independently, at different times, by different code paths (`report_renderer.py`, `visualization.py`, `src/taxonomy_generator/evaluation/runner.py`, `main.py`'s own save block), and nothing in this codebase assigns a shared run ID across them. Given only a taxonomy JSON's path, `discover_siblings` (`html_report.py:256`) has to find which files in that same directory actually belong to it — degrading each sibling independently to "not available" rather than raising when a match is missing or ambiguous.

## Guidance

**Prefer explicit provenance over filename heuristics when it exists.** The evaluation JSON already stores a `source_file` field pointing at the exact taxonomy JSON it scored (`src/taxonomy_generator/evaluation/runner.py`'s saved artifact shape). `_evaluation_matches_source` (`html_report.py:160`) matches on that field by basename before falling back to any filename pattern — an explicit backlink beats a guess every time it's available.

**When no such backlink exists, prefer the embedded filename timestamp over filesystem mtime.** `main.py:run()` writes several sibling files reusing one `timestamp` variable inside a single `if args.output:` block (`main.py:1278` and the writes that follow it in the same call), so a report/documents file sharing the taxonomy JSON's exact embedded timestamp is a strong same-run signal. `_pick_candidate` (`html_report.py:53`) tries that exact match first. Filesystem mtime is the weaker fallback, used only when no candidate's filename carries a parseable timestamp at all — a plain file copy (exactly what test fixtures do) resets mtimes and would silently break an mtime-only strategy.

**Never match a numeric ID segment (like an iteration number) via glob wildcard or substring.** The biplot resolver originally globbed `*_{iteration}*`, which is a substring match in disguise: `"_1" in "taxonomy_biplot_name_standalone_10_2d"` is `True` in Python, so requesting iteration 1 could silently match a file actually written for iteration 10 (or 11, 19, 100, ...) with no warning, because it looked like a clean single-candidate match. `_biplot_filename_re` (`html_report.py:118`) fixes this by anchoring a regex against the full filename structure and capturing the iteration as its own group, so `resolve_biplot_path` (`html_report.py:132`) compares `int(match.group("iteration")) == target_iteration` — never a string fragment.

**When several generated sections must describe the same resolved state, thread it through once — never let a section re-derive its own copy.** A related bug in the same feature, outside the discovery module itself: `render_run_summary` (`html_report.py:412`) originally recomputed its own idea of "the current dimensions" straight from the taxonomy JSON, using different precedence than the rest of the page (which correctly used the pipeline's post-dimension-selection view). The two could disagree — Run Summary would list a dimension that the Discarded Dimensions section, on the same page, said was excluded. The fix changed the function's signature to accept the already-resolved view as a parameter instead of recomputing it, so agreement is guaranteed by construction rather than by keeping two copies of the same precedence rule in sync by hand.

## Why This Matters

Fail-soft resolvers that quietly pick a *wrong* match are worse than resolvers that report no match at all — a wrong match looks like success (a chart renders, a table populates) while showing data from a different run, and nothing in the UI signals the mismatch. The numeric-ID bug above is exactly that failure mode: no exception, no log line above debug level, just the wrong iteration's biplot rendered as if it were correct. Testing against real accumulated output directories, not only clean synthetic ones, is what surfaces this class of bug: `examples/cursor-git-at-scale/` has two evaluation JSONs whose `source_file` both point at the same taxonomy JSON (from running `--evaluate` twice) and both a 2D and 3D biplot for the same stage and iteration — real ambiguity a single synthetic fixture wouldn't have exercised.

## When to Apply

- Any new sibling-artifact type added to the unified HTML report (or a similar composition point) should get its own resolver following this same tie-break order: explicit backlink field, if the artifact type has one → embedded filename timestamp exact match → embedded filename timestamp newest-of-several → filesystem mtime only as the last resort.
- Any resolver or filter keyed on a numeric ID embedded in a filename must parse it with an anchored regex and compare as `int(...) == target`, never `in`/glob-substring.
- Any generated document with multiple sections that must agree on "the current view" of some resolved state should resolve that state once, at the call site that composes the whole document, and pass it down — not give each section its own derivation of the same precedence rule.

## Examples

Before (substring match, silently wrong for iteration 1 when only iteration 10+ exists):

```python
pattern = f"taxonomy_biplot_{name}_*_{iteration}*.html"
candidates = sorted(directory.glob(pattern))
```

After (`html_report.py:118-146`, anchored regex + integer compare):

```python
def _biplot_filename_re(taxonomy_name: str) -> re.Pattern:
    return re.compile(
        rf"^taxonomy_biplot_{re.escape(sanitize_filename_component(taxonomy_name))}_"
        r"(?P<stage>[A-Za-z]+)_(?P<iteration>\d+)_(?P<dims>\d+)d$"
    )

def resolve_biplot_path(directory, taxonomy_name, iteration):
    stem_re = _biplot_filename_re(taxonomy_name)
    matches = [
        (candidate, m)
        for candidate in sorted(directory.glob(f"taxonomy_biplot_{sanitize_filename_component(taxonomy_name)}_*.html"))
        if (m := stem_re.match(candidate.stem)) and int(m.group("iteration")) == iteration
    ]
    ...
```

Before (`render_run_summary` re-deriving its own view, `html_report.py`, pre-fix):

```python
def render_run_summary(taxonomy_data, documents_data):
    iterations = taxonomy_data.get("iterations") or []
    final_clusters = (
        iterations[-1]["clusters"] if iterations else (taxonomy_data.get("selected_clusters") or [])
    )
    ...
```

After (`html_report.py:412`, the caller's already-resolved view passed in):

```python
def render_run_summary(taxonomy_data, view_clusters, documents_data):
    # view_clusters is the same resolved dimension view (selected_clusters
    # when present, else the last iteration) passed to Diagram/Catalog/Discarded.
    ...
```

## Related

- `docs/solutions/architecture-patterns/surface-langgraph-node-output-through-state-schema-to-cli-and-report.md` — a different composition problem in the same feature area (getting a new node-produced value through `State`/`OutputState` and `main.py`'s manual `astream` accumulation into the saved JSON and report). Related by module and by "getting a value from where it's produced to where it's rendered," but a distinct mechanism: that doc is about crossing the LangGraph schema/CLI-accumulation boundary for a value not yet in any file; this one is about matching values that are already in separate files with no run ID connecting them.
- `docs/solutions/architecture-patterns/taxonomy-evaluation-suite-scoreboard-and-consistency.md` — defines the evaluation scoreboard artifact's own shape (including `source_file`) that this pattern's evaluation resolver depends on.
- Plan: `docs/plans/2026-09-03-0846-feat-unified-html-report-plan.md`, KTD1 (Planning Contract) — the original design of this matching heuristic.
