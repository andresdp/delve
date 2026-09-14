---
title: --html-report Ignored a Taxonomy JSON's Own Embedded Evaluation Scoreboard
date: 2026-09-05
category: logic-errors
module: html_report
problem_type: logic_error
component: service_layer
symptoms:
  - "A fresh `--output` pipeline run with evaluation enabled saves a taxonomy JSON whose `evaluation` key holds a real, populated scoreboard (`criteria`, `overall`, `model`, `unavailable: false`)"
  - "Running `--html-report` against that exact same taxonomy JSON renders \"No evaluation was run for this taxonomy\" in the Evaluation section, even though the scoreboard is present in the file being rendered"
  - "The gap only shows up once a live pipeline run actually produces an in-run `evaluation` key — it was invisible before that, since `evaluate_taxonomy` was previously dead code in `graph.py` (see Related)"
root_cause: logic_error
resolution_type: code_fix
severity: medium
tags: [html-report, evaluation, sibling-artifact-discovery, taxonomy-json, main-py, fallback]
---

# --html-report Ignored a Taxonomy JSON's Own Embedded Evaluation Scoreboard

## Problem

`main.py::_run_html_report` builds the unified HTML report's evaluation section exclusively from a **sibling** `evaluation_*.json` artifact discovered on disk (via `html_report.discover_siblings` → `resolve_evaluation_path`, matched by `source_file`/`taxonomy_name`/`iteration`). That sibling file is only ever written by the separate, standalone `--evaluate` CLI mode. It never considered the **taxonomy JSON's own `evaluation` key**, which is what a live `--output` pipeline run with evaluation enabled actually writes (`main.py::run()`: `if evaluation is not None and not evaluation.get("unavailable"): taxonomy_data["evaluation"] = evaluation`). Two independent code paths write evaluation data in two different shapes and locations, and the report renderer only knew about one of them.

## Symptoms

- `--html-report <taxonomy.json>` prints `No evaluation sibling found — that section will show as unavailable.` and the rendered page shows "No evaluation was run for this taxonomy" (the `render_evaluation_section(None)` branch in `html_report.py`).
- The same taxonomy JSON, opened directly, has a fully populated `evaluation` key: `{"criteria": [...], "overall": 0.47, "model": "openai/gpt-5.6-luna", "unavailable": false}`.
- The gap is easy to miss because it degrades to a plausible-looking "no evaluation" message rather than an error — there's no signal that data existed but wasn't used.

## What Didn't Work

Nothing prior — this was caught by directly comparing the generated HTML report's rendered section against the taxonomy JSON's own contents after a live run, rather than trusting the report's "no evaluation" message at face value.

## Solution

`main.py::_run_html_report` now falls back to the embedded key, wrapped in the same shape `render_evaluation_section` already expects from a sibling artifact, when no sibling matched:

```python
evaluation_data = siblings.evaluation.data if siblings.evaluation else None
used_embedded_evaluation = False
if evaluation_data is None and isinstance(data, dict) and data.get("evaluation"):
    # No standalone evaluation_*.json sibling matched (that mode is a
    # separate --evaluate CLI run), but a live pipeline run with
    # evaluation enabled embeds its own scoreboard directly in the
    # taxonomy JSON — wrap it in the same shape render_evaluation_section
    # expects from a sibling artifact rather than leaving it unused.
    evaluation_data = {"scoreboard": data["evaluation"]}
    used_embedded_evaluation = True
```

The console notice for the "no sibling found" case was also updated to distinguish "using the embedded evaluation" from a genuine "no evaluation anywhere" case, so the operator isn't told data is missing when it was actually just found somewhere else.

Verified: regenerating the html-report from an existing taxonomy JSON (no LLM calls needed for this step) now renders the full Evaluation section — overall score, judge model, and a per-criterion table with score/pass/rationale — sourced from the embedded key.

## Why This Works

`render_evaluation_section` already only cared about the `{"scoreboard": {...}}` shape, regardless of where that dict came from — so the fix needed no changes to the rendering logic itself, only to which source `_run_html_report` reads before calling it. The embedded key and the sibling artifact both ultimately carry the exact same `run_scoreboard()` return shape (`{"criteria", "overall", "model", "unavailable"}`); the sibling file just adds a `{"source_file", "taxonomy_name", "iteration", "scoreboard": ...}` wrapper around it. Reusing that same wrapper for the embedded case means the renderer needs no branching on where the data came from.

## Prevention

- When a feature grows a second way to produce the same conceptual data (here: an in-run embedded scoreboard vs. a standalone artifact file, added at different times by different plans), audit every **consumer** of that data for whether it checks both sources, not just the one that existed when the consumer was written.
- A resolver that degrades silently to "not available" (by design, per the fail-soft convention this codebase uses throughout `html_report.py`) can hide exactly this kind of gap — the failure mode looks identical to "there's genuinely no data," so it's worth testing the discovery step directly against a taxonomy JSON you know has the data, rather than trusting the rendered page's absence-of-error as proof of correctness.
- This bug was invisible before this session because it required a live pipeline run that actually populates the taxonomy JSON's `evaluation` key — which required first fixing the fact that `evaluate_taxonomy` was dead code in `graph.py` (see Related). A code path with no real test coverage and a fail-soft default can carry a bug like this indefinitely without a live end-to-end run to expose it.

## Related Issues

- `docs/solutions/architecture-patterns/sibling-artifact-discovery-without-shared-run-id.md` — documents the sibling-matching heuristics (`discover_siblings`, `resolve_evaluation_path`) this fix adds a fallback alongside. Moderate overlap: same problem area (evaluation-section sourcing for the unified HTML report), different root cause (that doc is about matching *across* independently-written sibling files; this bug is about never checking a *self-contained* source at all) — kept as a separate doc rather than merged, per that distinction.
- `docs/solutions/architecture-patterns/taxonomy-evaluation-suite-scoreboard-and-consistency.md` — the evaluation suite whose in-graph wiring being previously dead code is why this gap was invisible until now.
- Fixed on branch `feat/taxonomy-evaluation-feedback-integration` (commit `83dacf2` as of this writing, pushed to `origin`, PR not yet opened).
