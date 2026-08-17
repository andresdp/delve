---
title: Narrative Summary Referenced Dimensions Excluded From the Rendered View
date: 2026-08-16
category: logic-errors
module: report_renderer
problem_type: logic_error
component: service_layer
symptoms:
  - "Generated grounded-theory report's narrative section mentions or describes a dimension that does not appear anywhere in the report's mermaid diagram or dimension catalog"
  - "Narrative text is inconsistent with the accompanying deterministic structural sections when the report is rendered for a filtered dimension selection (selected_clusters)"
  - "Report readers see the narrative referencing taxonomy structure that was deliberately excluded from the current view"
root_cause: logic_error
resolution_type: code_fix
severity: medium
tags: [narrative-summary, dimension-scoping, llm-context-filtering, grounded-theory-report, prompt-instruction-fix, report-renderer, taxonomy-generator, selected-clusters]
---

# Narrative Summary Referenced Dimensions Excluded From the Rendered View

## Problem

`generate_narrative_summary` (`src/taxonomy_generator/report_renderer.py:191-243`) fed its LLM call two context sources meant to describe the same rendered view — an in-scope `clusters` list and a free-text `explanation` string — but only the `clusters` list was actually scoped to that view; `explanation` was resolved separately in `main.py` and could still reference dimensions the view no longer included, letting the generated narrative describe structure absent from the diagram/catalog directly beneath it in the same report.

## Symptoms

- When the rendered view is `selected_clusters` (a filtered subset chosen by a dimension-selection step) rather than a full iteration, the narrative summary section of the generated report could name or describe a dimension that does not appear in the "Dimension Relationship Diagram" or "Dimension Catalog" sections that follow it in the same document.
- The mismatch was silent: `generate_narrative_summary` has no validation step (`report_renderer.py:220-243` is a bare try/except around the model call, catching only outright failures and returning `None`, not a content check), so a leaking reference would ship in the written report file with no warning or error.
- Root cause was traceable to `_explanation_for_view` in `main.py:499-526`: for the default (no `--iteration`) case it falls back to `iterations[-1].get("explanation")` (`main.py:525`) — the *latest* iteration's explanation — regardless of whether the rendered `clusters` came from that same iteration or from an earlier, narrower `selected_clusters` snapshot, so the explanation text and the dimension list could describe different points in the taxonomy's history.

## What Didn't Work

- Programmatically pre-filtering the free-text `explanation` string (e.g., regex-stripping sentences that mention an excluded dimension name) was considered and rejected as unreliable — prose doesn't have a stable, matchable structure the way a dimension list does, so a regex/string-matching pass would both miss paraphrased references and risk mangling legitimate sentences.
- Three smaller, unrelated defects were also caught in the same review pass and fixed alongside this one (see Solution for specifics): an unhandled `SystemExit` on the auto-report path that could abort an otherwise-successful `--output` run, a mermaid-label escaping gap that only handled quotes and not embedded newlines, and a `dict.get(key, default)` misuse that let an explicit JSON `null` leak through as the literal string `"None"`.

## Solution

The fix does not touch `report_renderer.py`'s call-construction code at all — it closes the gap entirely inside the prompt, `src/taxonomy_generator/prompts/narrative_summary.md`, by adding an explicit instruction that names "Dimensions" as the sole source of truth over "Taxonomy Explanation":

> "**The "Dimensions" section is the sole authority on what exists in this view.** The "Taxonomy Explanation" text may have been written for an earlier or broader version of the taxonomy and can reference dimensions that are no longer part of this rendered view. Ignore any such reference — do not carry a dimension, relation, or value into your summary unless it also appears in "Dimensions"."

This sits alongside the prompt's pre-existing "Never invent structure" guideline (`narrative_summary.md:22`), and both inputs (`explanation`, `dimensions`) are still passed through unfiltered from `generate_narrative_summary` (`report_renderer.py:230-235`) and from `_run_report`/`run()` in `main.py` (`main.py:597-598`, `main.py:942-954`) — only the prompt's handling of them changed.

The three supporting defects, fixed in the same pass:
1. `main.py:939-950` — the auto-report branch inside `run()`'s `--output` block now wraps the `_select_clusters_for_visualize` call in `try`/`except SystemExit`, logging a warning and skipping the report (`main.py:945-949`) instead of letting an out-of-range `--iteration` abort a run after the four core artifacts (documents/taxonomy/messages/clusters) were already saved.
2. `_escape_mermaid_label` (`report_renderer.py:53-60`) now collapses `"\r\n"`, `"\n"`, and `"\r"` to spaces in addition to escaping `"`, so an embedded newline in a dimension name can no longer split a mermaid label across two physical lines.
3. `_cluster_id` and `_relation_target_id` (`report_renderer.py:33-40`) now use `cluster.get("id") or "?"` / `relation.get("target_id") or ""` — matching the `.get(key) or default` idiom already used throughout the same file for `name`/`description`/`relation_type` fallbacks (e.g. `report_renderer.py:86,131-132,161-162`) — so an explicit JSON `null` correctly falls through to the default instead of stringifying to `"None"`.

## Why This Works

The underlying principle: when one LLM call is fed two context sources meant to describe the same scope, but the sources are of different *shapes* — one structured/filterable (a list of dimension dicts, easy to subset with a Python filter before it ever reaches the prompt) and one free-text/unfilterable (an LLM-written paragraph, with no reliable machine-checkable structure to filter on) — filtering only the structured source is not enough. The free-text source can still leak references to whatever was filtered out, because nothing filters prose reliably. Each input crossing the trust boundary into the same prompt needs its own explicit scoping treatment; you cannot assume that constraining one input transitively constrains the other just because they end up in the same call.

The fix is cheap specifically because it reuses a mechanism this feature's own plan had already accepted as sufficient for a harder, adjacent problem. KTD7 in the plan (`docs/plans/2026-08-16-2115-feat-grounded-theory-report-plan.md:167`) already accepted "prompt instruction only, no post-hoc validation" as the enforcement mechanism for R10 — "never let the LLM invent structure that doesn't exist at all" (`docs/plans/2026-08-16-2115-feat-grounded-theory-report-plan.md:54`). Since that risk tier was already accepted for the general case, applying the same mechanism (an explicit instruction, no new validation code) to this narrower, second leakage path was consistent with the codebase's established risk posture rather than a new exception to it — closing the gap with a one-line prompt addition instead of inventing new filtering code.

## Prevention

- When a plan's Key Technical Decision states that a value should be "scoped" to a view (here, KTD5 at `docs/plans/2026-08-16-2115-feat-grounded-theory-report-plan.md:165`: "scoped to omit any dimension not present in the rendered `selected_clusters` set"), check during review whether that scoping was applied to *every* input crossing the same boundary into the same downstream consumer — not just the most obviously structured one. A `clusters` list being filtered correctly is not evidence that `explanation` was filtered too; verify each input independently.
- When an LLM call combines a structured input with a free-text input describing the same scope, treat the free-text input as requiring its own explicit prompt-level constraint by default — don't assume filtering the structured side is sufficient, since prose can't be reliably filtered programmatically the way a list can.
- Use `dict.get(key) or default`, not `dict.get(key, default)`, whenever an explicit JSON `null` should be treated the same as an absent key — `.get(key, default)` only substitutes the default when the key is missing entirely, letting a `null` value pass through unmodified (and, if later stringified, become the literal text `"None"`). `report_renderer.py` already had this idiom established for `name`/`description` fallbacks (e.g. `report_renderer.py:86,131-132`); the bug was one call site (`_cluster_id`/`_relation_target_id`) not following a pattern already present two lines away in the same file — worth a quick grep for `.get(` with a literal default when reviewing similar dict-parsing code.

## Related Issues

Found during code review (`ce-code-review`) of branch `feat/grounded-theory-report`, prior to merge. Plan: `docs/plans/2026-08-16-2115-feat-grounded-theory-report-plan.md`. No external issue tracker entry exists for this — the branch's own commit `73defdc` ("fix(report): address code review findings") is the fix record.
