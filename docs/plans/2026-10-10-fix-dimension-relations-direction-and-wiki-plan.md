---
title: "fix: consistent, correctly directed dimension relations, explained and filterable in the wiki"
type: fix
status: planned (not started; to do on a quick feature branch, e.g. feat/dimension-relations)
date: 2026-10-10
related: >-
  src/taxonomy_generator/{schemas,tool_update,taxonomy_editor,utils,html_report,report_renderer}.py,
  src/taxonomy_generator/nodes/dimension_merger.py, src/taxonomy_generator/evaluation/design_points.py,
  src/taxonomy_generator/prompts/{taxonomy_generation,taxonomy_update,taxonomy_tools,taxonomy_review,narrative_summary}.md,
  src/taxonomy_generator/wiki/{model.py,templates/graph.html.j2,templates/tree.html.j2}
---

# Consistent dimension relations, explained and filterable in the wiki

## Goal

Keep relations **between dimensions only**, with 4 types (5 with the optional `refines`), and make them:

1. **consistent and correctly directed** when the LLM creates them;
2. **explained** in the wiki (what each type means, how to read an arrow);
3. **hideable** in the wiki's graph view when they clutter it.

**Out of scope:** relations between values (excludes/requires between alternatives, option → follow-up decision),
grounding relations in passages, comparing relations with the expert models, and any claim about relations in the
paper. These remain ideas for later (see the end).

## Problem (measured 2026-10-10 on the main runs)

| Run | Dimensions | Relations | Notes |
|---|---|---|---|
| C1 `c1-u7b-tools` | 30 | 156 (73 precondition, 50 constrains, 22 consequence, 11 co_occurring) | 29 dimensions have relations; 24 pairs related both ways |
| C2 `c2-u7b-tools-norelevance` | 19 | 154 (spread over all 4 types) | About 8 per dimension; 56 pairs related both ways: nearly complete |
| C3 `c3-git-at-scale_…_115350` | 22 | 25 (no `constrains`) | One relation points to a dimension that no longer exists |

- **Reversed direction.** The schema says `precondition` means "a choice on the target is required before the source
  applies", yet runs contain e.g. "Data Profiling and Validation → precondition → Training Update Algorithm" with the
  rationale "validated features are prerequisites for training" (reversed), and in C2 "Safety Assessment Standard →
  consequence → Reward Model Construction" justified by reward design causing safety failures (reversed). The model
  reads "A → B" as "A relates to B" and argues either way.
- **Too dense** to carry information (C2).
- **Validation gaps:** the editor rejects self-loops, unknown types and exact duplicates only; nothing stops opposite
  pairs, cycles, very dense relation sets, or targets removed later in rewrite mode.

## Decisions

| # | Decision |
|---|---|
| R1 | Relations stay **dimension → dimension**. |
| R2 | Types are named so that every relation **reads left to right** as "source *verb* target" (table below). The meaning of the existing types is unchanged: this is a rename plus clearer wording. |
| R3 | Consistency is enforced by **structure and validation**, not by prompt wording alone: a required reading sentence checked by code, editor checks, and a cap per dimension. Prompts explain the same rules. |
| R4 | The wiki explains relations on a reference page and writes them as sentences everywhere. |
| R5 | The graph view can hide relations (all, per type, or all but the selected dimension's) without moving the layout. |

### Relation types

| Old name | New name | Reads as | Directed | Arrow in the graph |
|---|---|---|---|---|
| `precondition` | `requires` | "A **requires** B to be decided first" | yes | A → B |
| `consequence` | `affects` | "Choices on A **affect** the outcomes of B" | yes | A → B |
| `constrains` | `constrains` | "Choices on A **limit** the options available on B" | yes | A → B |
| `co_occurring` | `co_occurs_with` | "A and B are **usually decided together**" | no (stored once per pair, lower id as source) | A — B, no arrowhead |
| – | `refines` *(optional, behind a setting)* | "A **is a sub-decision of** B" | yes | A → B |

`refines` is off by default (`taxonomy.relation_types` lists the allowed types; default the first four). Turn it on
only if the C1-style cross-cutting dimensions need it.

Old runs: a mapping `precondition → requires`, `consequence → affects`, `co_occurring → co_occurs_with` is applied
when a saved taxonomy is loaded (seeding, `--evaluate`, wiki export, reports), so old and new runs render the same way.
Direction is kept as stored (old runs keep any reversals; the wiki cannot fix them).

## Implementation units

### U1. Schema, reading sentence and old-run mapping

- `schemas.py`: `RelationType` = the new names (plus `refines`); `Relation` gains `reading: str`, described as "the
  relation written as one sentence with the two dimension names, in the form given for its type".
- One shared module (e.g. `src/taxonomy_generator/relations.py`):
  - the type table (name, sentence template, directed or not), used by prompts, editor, wiki and reports;
  - `render_reading(source_name, type, target_name)` → the canonical sentence;
  - `normalize_type(old_or_new)` for old runs;
  - `check_reading(reading, source_name, target_name, type)`: the two names appear in the right order and the type's
    verb phrase is between them (case- and punctuation-insensitive, tolerant of small name variations via the
    canonical sentence). Returns a reason when it fails.
- `tool_update.py` `AddRelation`: field descriptions from the shared table; add `reading`; the direction stated in
  words ("source = the dimension that requires / affects / limits; target = the one required / affected / limited").
- **Tests:** templates for every type; the mapping; `check_reading` accepts the canonical sentence and paraphrases with
  the names in order, rejects swapped names and the wrong verb.

### U2. Editor checks (tools and rewrite mode)

In `TaxonomyEditor` (tools mode) and wherever rewrite-mode output is parsed into clusters (`utils.py`; verify the
exact function), apply the same checks:
- unknown dimension, self-loop, unknown or disabled type (existing);
- **reading sentence fails** `check_reading` → rejected with the canonical sentence in the error, so the model can
  retry with the correct direction ("did you mean: '<B> requires <A> to be decided first'?");
- **opposite pair** of the same directed type (A requires B and B requires A) → rejected;
- **cycle of `requires`** (A → B → … → A) → rejected;
- `co_occurs_with` normalized to one stored relation per pair;
- **cap** `taxonomy.max_relations_per_dimension` (default 3, counting outgoing relations; `null` = no cap) → rejected
  with a message asking to remove a weaker one first;
- after `merge_dimensions`, `remove_dimension` and the dimension merger node: redirect, then drop self-loops and
  duplicates created by the merge, and re-check opposite pairs (keep the first).
- In rewrite mode (no retry loop), invalid relations are **dropped and logged** in the operation log/status, not fatal.
- **Tests** (`test_taxonomy_editor.py`, `test_tool_update.py`, merger tests): each rejection; the cap; the merge
  cleanup; the rewrite-mode drop path.

### U3. Prompts

Same short block in `taxonomy_generation.md`, `taxonomy_update.md`, `taxonomy_tools.md` and `taxonomy_review.md`,
rendered from the shared table (U1) so the wording never diverges:
- the type table with the reading sentences;
- "write the `reading` sentence first; it must be true for the use case as written; if it only holds the other way,
  swap source and target";
- one correct example and one reversed example with its fix (generic, not from a study, to avoid leaking a case);
- "at most N relations per dimension (N = the cap); keep only the interactions the sources discuss; a relation that
  only says two topics are related is not a relation";
- `co_occurs_with` only when the sources show the two decisions being made together.
- `narrative_summary.md`: refer to relations by their reading sentences.
- `test_prompt_content.py`: the block is present in each prompt and matches the table.

### U4. Wiki: explanation and sentences

- **Reference page** `wiki/reference/relations.md` (OKF `type: Reference`; HTML too), linked from the overview, the
  Approach page and the graph legend. Content: the type table; how arrows are drawn; one real example per type from the
  current run (when present); the note that relations are inferred by the model from the use case and the sources'
  topics and are **not** checked against passages the way values are; the cap and the validation rules in one line each.
- **Dimension pages:** "Relations from this dimension" and "Relations to this dimension", each item a sentence with the
  other dimension linked and the rationale below, e.g. "**Requires** [Data Profiling and Validation] to be decided
  first" / "[Training Update Algorithm] **requires** this dimension to be decided first".
- **Graph tooltips and tree view:** the same sentences instead of the type code.
- Old runs go through the type mapping (U1) before rendering.
- **Tests** (`test_wiki_export.py`): the reference page exists and is linked; sentences for each type in both
  directions; a run with old type names renders with the new sentences.

### U5. Graph view: hide or filter relations

In `graph.html.j2`:
- a **"Dimension relations"** fieldset in the filter panel: a master checkbox, one checkbox per type, and **"only for
  the selected dimension"**;
- a legend: one dash style or shade per type; arrowheads on directed types, none on `co_occurs_with`;
- **hiding does not move the layout:** hidden relation edges keep their force in the simulation (only their drawing is
  hidden). A **"re-layout without relations"** button restarts the simulation without them;
- **default:** relations shown when the run has at most 2 relations per dimension on average; otherwise
  "only for the selected dimension" is on, with a one-line note saying why. The threshold is a page constant;
- filter changes clear the selection, as the other filters do.
- **Tests:** the exported graph data carries the relation type and reading sentence on each relation edge; the template
  contains the controls (string checks, as the existing wiki tests do). Manual check in a browser on C2 (dense) and
  C3 (sparse).

### U6 (optional). Direction check after a run

`benchmark/relation_check.py <run>`: for each relation, ask the judge (one yes/no per relation, OpenAI; later possibly
Jev) whether the reading sentence holds for the use case; if not, whether the reversed sentence holds. Report kept /
flipped / dropped counts; with `--apply`, write a corrected copy of the run (never overwrite). Use it to measure the
effect of U1–U3 on a re-run, and on the old runs.

## Effort

| Unit | Effort |
|---|---|
| U1 + U2 + U3 (pipeline) | 1–1.5 d |
| U4 + U5 (wiki) | 1 d |
| U6 (optional) | 0.5 d |

## Order and timing

- **U4 and U5 first:** they only touch the wiki, work on existing runs (through the mapping), and can merge any time.
- **U1–U3 change generation:** runs before and after are not comparable. Merge into `main` only after the paper's main
  runs are done (relations are out of the paper's scope), or keep the branch until then.
- Validation on one small re-run (C3, about 5 dimensions) before merging: no reversed readings in a hand check of all
  relations; average relations per dimension at or below the cap.

## Later (not in this plan)

Value-level dependencies (excludes, requires, opens a follow-up decision), grounding relations in passages,
co-adoption computed from evidence, dimension relations derived from value-level ones, comparison with the expert
models' decision links (C1: 40 "Consider If Not Decided Yet"; C2: 6 typed links), and design points that respect
constraints.
