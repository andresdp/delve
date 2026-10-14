---
title: "LLM-inferred dimension relations: reversed direction and split fan-out, fixed by structural checks at every entry point"
date: 2026-10-10
category: logic-errors
module: taxonomy_generator
problem_type: logic_error
component: service_layer
symptoms:
  - "Relations stored with reversed direction, e.g. Data Profiling and Validation -precondition-> Training Update Algorithm justified as validated features being prerequisites for training (the opposite of the type's meaning)"
  - "Dense relation graphs with pairs related both ways (C2: 154 relations over 19 dimensions, 56 both-way pairs) and dangling targets"
  - "After a split, one relation became several copies with the same rationale, a dimension exceeded the relation cap, and stored reading sentences named retired dimensions"
  - "Defining the relation types more carefully in the prompts did not fix the direction errors"
root_cause: missing_validation
resolution_type: code_fix
severity: high
related_components:
  - taxonomy_editor
  - dimension_merger
  - report_renderer
  - wiki
tags: [relations, dimension-relations, llm-output-validation, relation-direction, split-dimension, rewrite-mode, taxonomy-generator]
---

# LLM-inferred dimension relations: reversed direction and split fan-out, fixed by structural checks at every entry point

## Problem

LLM-inferred relations between taxonomy dimensions (design-space "decision points") were unreliable in two stages. First, the model stored many of them with the wrong direction. Second, after the direction fix, structural edits (split, merge, rename) multiplied relations or left them stale. Both fixes are on branch `feat/dimension-relations` (local, not merged).

## Symptoms

- **Reversed direction.** "Data Profiling and Validation -precondition-> Training Update Algorithm" was justified as "validated features are prerequisites for training". The schema meaning was the opposite: a choice on the *target* is required before the *source* applies. In C2, "Safety Assessment Standard -consequence-> Reward Model Construction" was justified by reward design causing safety failures. The model reads "A -> B" as "A relates to B" and argues either way.
- **Dense, both-way graphs.** C1 had 156 relations over 30 dimensions. C2 had 154 over 19, with 56 pairs related both ways. C3 had 25 over 22, with 10 both-way pairs and 1 dangling target.
- **Fan-out after the first fix.** A C3 re-run produced 41 relations from about 10 distinct ones. One relation became 2 x 4 = 8 copies with the same rationale. One dimension held 4 relations against a cap of 3. 25 of the 41 stored reading sentences named pre-split or pre-rename dimensions.

## What Didn't Work

- **Defining the four (old) relation types more carefully in the prompts.** They were already defined, and the model still inverted them. Wording alone did not enforce direction.
- **Checking the rules only in the editor's `add_relation` tool.** Splits, merges, rewrite output and seed loading each created or copied relations without going through that path, so the per-dimension cap and duplicate rules were bypassed.
- **Unit tests alone.** All passed while the split fan-out existed. It only showed up when re-running C3 and counting relations.

## Solution

**1. Make direction structural.** `src/taxonomy_generator/relations.py` holds one table, `RELATION_KINDS` (line 41). Each type has a template that reads left to right, "source <verb> target" (`requires`, `affects`, `constrains`, `co_occurs_with`, `refines`). Legacy names (`precondition`, `consequence`, `co_occurring`) are mapped by `normalize_type`. Each new relation carries a `reading` sentence. `check_reading` (line 154) returns an error unless (for directed types) the source name comes first, then the type's verb, then the target name. It tells the model when the reading is reversed. `relation_problem` (line 207) rejects unknown or disabled types, duplicates, opposite pairs, `requires` cycles, relations past the cap, and a bad reading. Its error message includes the canonical sentence to write. `co_occurs_with` is undirected and stored once on the lower id (`canonical_ends`, line 91).

**2. One guide, rendered from the table.** `read_prompt_file` (`src/taxonomy_generator/prompts/__init__.py:17`) replaces `RELATION_GUIDE_MARKER` (line 14) in every prompt file with `relation_guide(...)`, so prompt text and code cannot drift.

**3. Run every entry point through `clean_relations` (`relations.py:263`).** It replays relations in order against `_problem`, drops violations (returning them with reasons), and re-renders each kept relation's `reading` from the current names. Callers:
- the editor, in `TaxonomyEditor.result()` (`src/taxonomy_generator/taxonomy_editor.py:545`, call at line 567, with `max_per_dimension=self.max_relations`), and also once when the editor loads the previous taxonomy (line 115, no cap);
- rewrite output, via `sanitize_relations` (`src/taxonomy_generator/utils.py:388`), called from `invoke_taxonomy_chain` (`utils.py:800`);
- seed loading, `load_seed_taxonomy` (`utils.py:404`; the `clean_relations(clusters)` call is at line 469). This path only normalizes saved runs (legacy names, opposite pairs, readings): it applies no cap and no reading check;
- dimension merging, `merge_groups` (`src/taxonomy_generator/nodes/dimension_merger.py:66`, after remapping targets).

**4. Stop the split fan-out.** Before, a split copied the relations to every part and pointed incoming relations at every part. Now only the first part keeps them, and the reply tells the model where they went:

```python
# taxonomy_editor.py _split_dimension (~line 442)
if not new_dims:  # relations stay with the first part only; copying them to every part multiplies them
    new["relations"] = copy.deepcopy(dim["relations"])
...
c["relations"] = [{**r, "target_id": new_ids[0]} if str(r.get("target_id")) == str(dim["id"]) else r ...]
```

**5. Trust relations already accepted in rewrite mode.** `sanitize_relations` passes `trusted=relation_keys(previous)` (`utils.py:400`). Those relations skip the reading check, because a renamed dimension would otherwise fail the old sentence and silently lose its relations. New relations are still checked. Trusted keys are `(source, target, type)` with canonical ends.

**6. Fix a reading-check edge case.** The reading check failed when one dimension name contains the other (both matched at token 0). Matching now takes the longer name first and excludes its span (`_positions` / `_find` in `relations.py`).

## Why This Works

- Direction is verified by code against a sentence the model has to write first. The model's reading of "A -> B" no longer decides what the relation means.
- The rules live in one function, `_problem`. Each entry point that can create or alter relations calls it through `clean_relations`, so edits cannot bypass the cap, duplicate or opposite-pair rules.
- Readings are re-rendered from current names, so they cannot go stale after a rename, split or merge.
- Trusting previously accepted relation keys separates "was this accepted before" from "does the sentence still match", which keeps renames from dropping relations.

Measured on a C3 run (one run per row, model gpt-5.6-luna, no dimension cap):

| Run | Relations | Max per dim | Both-way pairs | Duplicated rationales | Stale readings |
|---|---|---|---|---|---|
| 10-08, old rules | 25 | 7 | 10 | 20 | 24 |
| 10-10, before split fix | 41 | 4 | 0 | 33 | 25 |
| 10-10, after split fix | 11 | 1 | 0 | 0 | 0 |

In the after-split-fix run, all 11 directions read correctly against their rationales. Dimension counts varied (22/19/31) across runs, so the relation counts are not cleanly comparable. One run each, and the difference is not attributed to a single cause. The unit suite had 490 passing tests in this session's run.

## Prevention

- **Do not rely on prompt wording for direction.** Use a type table with a left-to-right template, require the sentence first, and check it in code.
- **Every code path that creates, copies, remaps or merges relations must end in `clean_relations`.** When adding a new structural edit, route its output through it and pass the cap; a loader of saved runs only needs the normalizing call.
- **Never copy relations to multiple parts of a split.** Keep them on one part and tell the model where they went.
- **Rewrite mode:** pass `trusted=relation_keys(previous)`. Do not re-check readings of relations that were already accepted.
- **Tests to keep or add** (see `tests/unit_tests/test_relations.py`, `test_relation_wiring.py`, `test_taxonomy_editor.py`):
  - `check_reading` accepts "A requires B to be decided first" for A -requires-> B and rejects the reversed sentence, with a message about the reverse direction.
  - `check_reading` works when one dimension name contains the other.
  - After splitting a dimension with N relations into k parts, the total relation count is unchanged and only the first part holds the outgoing ones.
  - After splits and merges, no dimension exceeds `max_relations_per_dimension` and no stored `reading` names a retired dimension.
  - Rewrite mode with a renamed dimension keeps its existing relations but still drops a new relation whose reading is reversed.
  - `co_occurs_with` given in either order is stored once, and `remove_relation` removes it in either order.
- **Measure on a real run.** After changing relation logic, re-run a sample taxonomy (for example C3) and count total relations, maximum per dimension, both-way pairs, duplicate rationales and stale readings. Unit tests missed the fan-out.

## Related Issues

- `docs/solutions/logic-errors/narrative-summary-includes-unscoped-explanation-text.md`: a sibling failure in the same
  report path. The narrative prompt was changed to quote relation sentences while its Dimensions input contained none
  (fixed on the same branch by listing in-view relation sentences under each dimension).
- `docs/solutions/ui-bugs/graph-filter-change-kept-stale-selection-fade.md`: the wiki graph's relation filters
  deliberately bypass the selection-clearing filter handler, so "only the selected dimension's relations" stays usable.
- Plan: `docs/plans/2026-10-10-fix-dimension-relations-direction-and-wiki-plan.md`.
