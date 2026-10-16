---
title: "refactor: a taxonomy data layer — one model, validated operations, pluggable storage"
type: refactor
status: proposed (2026-10-15); parked until after the SANER submission (2026-10-23), except U1 (safe, additive)
date: 2026-10-15
related: >-
  src/taxonomy_generator/{state,schemas,taxonomy_editor,tool_update,utils,relations,pipeline_cli}.py,
  src/taxonomy_generator/nodes/*.py, src/taxonomy_generator/evaluation/*.py, src/taxonomy_generator/wiki/*.py,
  src/delvedspace/{runs,wiki_build,check,point}.py, benchmark/replay_consolidation.py,
  docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md (the editor and the operation log)
---

# A taxonomy data layer

## Goal

Treat the design space (dimensions, values, evidence, relations) as a **data layer** that is separate from the
algorithms that change it, so that:

1. **Storage is pluggable.** The taxonomy can live in JSON files (as now), SQLite, a graph database or git, behind
   one interface.
2. **Algorithms are pluggable.** The mining workflow (LangGraph) becomes one producer of changes among others: a
   deterministic reorganizer, a merge of two taxonomies, a human through `ddspace`, an agent through tools.
3. **A taxonomy can start outside Delve.** A human or an agent can write one, or import one from the literature.
   Delve validates it and can then refine it.

The refactoring must not change any result the pipeline produces. In particular, the paper's C1–C3 numbers must
stay the same (see Verification).

## Current state (measured 2026-10-15, commit 4510f92)

- **There is no single in-memory model.** The Pydantic classes in `schemas.py` (`Value`, `Cluster`,
  `TaxonomyOutput` and 21 others) are LLM output schemas. Once parsed, the taxonomy is plain dicts:
  `State.clusters: Annotated[List[List[Dict]], operator.add]` (one snapshot per iteration), `selected_clusters`
  and `dropped_dimensions`.
- **The de facto data layer is the run file** `<name>_taxonomy_<timestamp>.json`, written by `pipeline_cli.run`.
  Top level: `taxonomy_name`, `mode`, `iterations[{explanation, clusters}]`, `selected_clusters`,
  `dropped_dimensions`, `evaluation`, `evaluation_history`, `operation_log`, `saturation_history`, `run_metrics`,
  `edit_mode`, `consolidated`.
  - Dimension keys: `id`, `name`, `description`, `values`, `relations`, `evidence`; rarely `merged_from`,
    `unsupported_values`, `hybrids`.
  - Value keys: `id`, `dimension_id`, `label`, `description`, `supporting_doc_ids`, `status`, `stances`,
    `evidence_code_count`, `merged_from`, `includes`.
  - Relation keys: `target_id`, `type`, `reading`, `rationale`.
  - Measured on 44 committed run files: 3,411 dimension and 33,852 value records.
- **An operations layer exists, but covers only part of the pipeline.** `TaxonomyEditor` offers 14 validated
  operations, each logged with its reason:
  - values: `add_value`, `add_evidence`, `move_value`, `merge_values`, `relabel_value`, `set_status`,
    `remove_value`;
  - dimensions: `add_dimension`, `rename_dimension`, `split_dimension`, `merge_dimensions`, `remove_dimension`;
  - relations: `add_relation`, `remove_relation`.

  It is used by `update_taxonomy` and `review_taxonomy` in `edit_mode: tools`. The paper configs (C1–C3) use tools
  mode; `config.yaml` and the `ddspace` template default to `rewrite`. `generate_taxonomy` always has the LLM
  write the whole taxonomy.
- **External loading half-exists.**
  - `utils.load_seed_taxonomy` accepts a run file or a bare list of dimension dicts (`--taxonomy`, `ddspace
    update`), so a hand-written JSON can seed a run today.
  - Its checks are only "non-empty and well formed"; the format is not documented as an interface.
- **Ids are display ids, not stable identities.** Dimensions are `"3"` and values `"3.1"`. Value recoding
  renumbers values, merges keep aliases only during one update, and `ensure_unique_ids` rewrites duplicates. A
  value's id can therefore change between iterations, so history and diffs match by name today
  (`wiki_build.diff`).

## Target architecture

| Layer | Responsibility | Built from |
|---|---|---|
| **Model** (`taxonomy_generator/model/`) | `Taxonomy`, `Dimension`, `Value`, `Relation`, `Stance`, `Hybrid` as Pydantic models; `validate()` for the invariants; lossless conversion to and from the dicts and the run file | `schemas.py` fields, the editor's rules, `relations.py` |
| **Operations** (`model/ops.py`) | Every change is an `Operation`: name, args, actor, reason, evidence refs. `apply(taxonomy, op)` validates, changes the taxonomy and appends to the log; errors are returned, not raised | `TaxonomyEditor` (atomic ops) + new **bulk ops** |
| **Store** (`model/store.py`) | `Store` protocol: `load(ref)`, `save(taxonomy, parent, log, meta)`, `history(ref)`, `diff(a, b)`. `FileStore` reads and writes today's run files | `pipeline_cli` writer, `load_seed_taxonomy`, `delvedspace.runs` |
| **Producers** | Anything that emits operations: LangGraph nodes, deterministic passes, `ddspace edit`/`import`, agent tools | the nodes |

### Key technical decisions

- **KTD1. The state keeps dicts at first; nodes convert at their boundary.** LangGraph reducers
  (`operator.add` on `clusters`) and checkpoint serialization stay as they are. A node calls
  `Taxonomy.from_dicts(state.clusters[-1])` and returns `taxonomy.to_dicts()`. Moving the state itself to model
  objects is a later, separate decision (U8).
- **KTD2. The run file format is the compatibility contract.**
  - `to_dicts(from_dicts(x)) == x` must hold for every committed run file: equal as parsed JSON (keys and values),
    not byte for byte.
  - Unknown keys are kept (`model_config = ConfigDict(extra="allow")`), so new keys added by a producer survive.
- **KTD3. Stable identity is separate from display ids.**
  - Each dimension and value gets a `uid` (a short random id): assigned when it is created, kept through
    relabel, move, merge (into the survivor's uid, with `merged_from` listing the others) and recoding (the new
    value has its own uid, with `includes` pointing to the old ones).
  - Display ids (`3.1`) stay what prompts, the wiki and users see.
  - The `uid` is written to the run file as an extra key; older files get uids on load, deterministically from
    their content, so loading twice gives the same uids.
- **KTD4. Bulk operations are first-class but validated.** Some passes rewrite a dimension as a whole: value
  consolidation (merge groups with stance union), evidence linking (attach many docs), value recoding (replace
  values), dimension merging, exclusivity repair. They become bulk operations with their own validation, logged
  as one entry each and expandable into atomic records for history. Forcing them into atomic calls would change
  their behavior, which KTD2 and the verification gate forbid.
- **KTD5. A rewrite becomes a diff.** In `rewrite` mode and in `generate_taxonomy`, the LLM's full taxonomy is
  turned into operations by a diff against the current one: `replace_taxonomy` at first, then a matcher that
  emits add, remove, move and relabel. Every edit mode then produces an operation log.
- **KTD6. The model is plain data plus pure functions, with no LLM inside.** LLM calls stay in producers, so any
  algorithm (LLM or not) drives the same layer.

## Operation inventory

These are the operations the data layer must offer: every read and write the pipeline, `ddspace` and the outputs
make on a taxonomy today, plus a few new ones. **R** = read (no change); **W** = write (validated, logged,
produces a new version).

- "Today" names the current code, so each operation has a known reference implementation for the equivalence
  gate.
- Ids are display ids (`3`, `3.1`), uids (KTD3) or names. Every operation that takes one resolves it through R6.

### Read operations

| # | Operation | Returns | Today |
|---|---|---|---|
| R1 | `get(view)`, where view = `final` \| `selected` \| `iteration n` | a `Taxonomy` snapshot | `state.clusters[-1]`, `selected_clusters`, `wiki.model.view_dimensions`, `resolve_seed_view` |
| R2 | `dimensions(core=, min_sources=)` | dimensions with counts, evidence, core flag | `query.dims`, `wiki.model.is_core` |
| R3 | `dimension(ref)` | one dimension with its values and relations | `query.show`, `editor._dim` |
| R4 | `values(dimension, status=)` | a dimension's values | `query.values` |
| R5 | `value(ref)` | one value | `editor._value`, `query.resolve` |
| R6 | `resolve(ref, kind)`: id, uid, slug, name, alias | one node, or the candidates | `query.resolve` (name matching), `editor.resolve_value` (aliases of moved and merged ids) |
| R7 | `candidates(dimension)` / `is_candidate(value)` | candidate decisions (accepted, rejected, mixed) vs outcomes | `CANDIDATE_STATUSES`, `CODING_CANDIDATE_STATUSES` |
| R8 | `evidence(value, stance=)` | passages by source, with stance | `query.evidence`, `value["stances"]` |
| R9 | `adopters(value, unit=source\|system)` | units whose accepted stance adopts it | `exclusivity.adopting_docs`, `unit_from_system_map` |
| R10 | `relations(from=, type=)` | relations with their reading sentence | `query.relations`, `relations.py` |
| R11 | `similar_values(label, scope)` | likely duplicates (lexical) | `taxonomy_editor.similar_values` |
| R12 | `metrics(...)`: exclusivity (dimension, taxonomy), generality, fragmentation, value combinations, recurring share, evidence rank | numbers and per-dimension rows | `evaluation/exclusivity.py`, `dimension_selector.rank_by_evidence` |
| R13 | `render(kind)`: kind = prompt \| compact \| judge \| report \| wiki \| graph | text or data for a consumer | `format_taxonomy`, `format_taxonomy_compact`, `taxonomy_prompt_view`, `format_taxonomy_for_judge`, `report_renderer`, `wiki.build` |
| R14 | `diff(a, b)` | added, removed, changed dimensions and values (by uid, falling back to name) | `saturation_checker` (`clusters[-1]` vs `[-2]`), `wiki_build.diff`, `delta_summary` |
| R15 | `history(ref)`, `log(ref)` | versions with their operations, actors and reasons | `iterations`, `operation_log` |
| R16 | `validate()` | problems (errors and warnings) | partly: the editor's checks, `clean_relations`, `load_seed_taxonomy` |
| R17 | `coverage(batch)` | batch documents not cited by any value | `editor.uncited_now` |
| R18 | `point(values)` / `sample_points(k, n, seed)` | a checked design point / sampled points | `query.point`, `evaluation/design_points.py` |
| R19 | `search(text, kind=)` | nodes by label or description | `query.search` |
| R20 | `with_linked_evidence(docs, codes)` | a **copy** with evidence linked, for scoring a draft; the taxonomy itself is unchanged | `taxonomy_evaluator._linked_draft` |

### Write operations

**Atomic** operations (exist in `TaxonomyEditor`; arguments as today):

| # | Operation | Arguments | Main rules (enforced today) |
|---|---|---|---|
| W1 | `add_value` | `dimension_id, label, description, doc_ids` | needs evidence from the batch; warns about similar values |
| W2 | `add_evidence` | `value_id, doc_ids` | docs must be batch documents |
| W3 | `move_value` | `value_id, to_dimension_id` | keeps an alias for the old id |
| W4 | `merge_values` | `value_ids, label, description` | one dimension, identical status |
| W5 | `relabel_value` | `value_id, label, description` | |
| W6 | `set_status` | `value_id, status, reason` | needs direct evidence outside the review |
| W7 | `remove_value` | `value_id` | never a value with supporting documents |
| W8 | `add_dimension` | `name, description` | |
| W9 | `rename_dimension` | `dimension_id, name, description` | |
| W10 | `split_dimension` | `dimension_id, parts[{name, description, value_ids}]` | each part keeps ≥ 2 candidate decisions |
| W11 | `merge_dimensions` | `dimension_ids, name, description, reason` | relations rewired |
| W12 | `remove_dimension` | `dimension_id` | only when empty |
| W13 | `add_relation` | `source_id, target_id, type, reading, rationale` | canonical direction, the reading checked (`relations.relation_problem`) |
| W14 | `remove_relation` | `source_id, target_id` | |

**New atomic** operations (done today by direct dict edits):

| # | Operation | Today |
|---|---|---|
| W15 | `declare_hybrid` / `remove_hybrid` (`dimension_id, value_ids`) | `dim["hybrids"]`, set by repair and dropped by recoding |
| W16 | `set_stance` (`value_id, doc_id, stance`) | `value["stances"]`, written by evidence linking and consolidation |

**Bulk** operations (KTD4). Each is one log entry with its own validation:

| # | Operation | What it does | Today |
|---|---|---|---|
| W17 | `create_taxonomy` / `replace_taxonomy` | a whole new taxonomy (first generation, a rewrite, an import); diffed into atomic records (KTD5) | `generate_taxonomy`, rewrite-mode `update`/`review`, `load_seed_taxonomy` |
| W18 | `link_evidence` | attach supporting docs, stances and counts for many values; recompute dimension evidence | `evidence_linker.link_evidence` |
| W19 | `remove_unsupported_values` | drop values with no supporting document after linking | `evidence_linker.drop_unsupported_values` |
| W20 | `consolidate_values` | merge synonym groups across stances (stance union; `mixed` status) | `value_consolidator._consolidate_values`, `_merge_group` |
| W21 | `merge_dimension_groups` | several `merge_dimensions` decided by one LLM call | `dimension_merger.merge_groups` |
| W22 | `replace_values` | recode a dimension's values as alternatives with `includes`; reassign evidence | `value_recoding.apply` |
| W23 | `merge_candidates` | the repair's stance-union merge | `exclusivity_repair.merge_candidates` |
| W24 | `rehome_values` | move many values at once (decision-focus variant) | `decision_focus.rehome_values` |
| W25 | `normalize`: unique ids, clean relations, recompute dimension evidence | idempotent repairs after any rewrite | `ensure_unique_ids`, `clean_relations`, `recompute_evidence` |
| W26 | `restore_dropped_values` / `carry_over_evidence` | put back evidence-bearing values a rewrite lost | `utils.restore_dropped_values`, `carry_over_evidence` (`rewrite_restore`) |

**Version and view** operations (the store, not the taxonomy's content):

| # | Operation | What it does | Today |
|---|---|---|---|
| W27 | `commit(taxonomy, explanation, actor)` | save a new version (an iteration) with its log | `state.clusters` append (reducer), `pipeline_cli` writer |
| W28 | `select(dimension_ids, dropped[{id, rationale}])` | set the reported view; the taxonomy is unchanged | `dimension_selector` (`selected_clusters`, `dropped_dimensions`, `apply_cap`) |
| W29 | `import(file)` | validate (R16) and create (W17) from an external file | partly: `load_seed_taxonomy`; new in U7 |

### Who uses which operation: LangGraph nodes

Nodes in graph order. "Via node" means the node's code applies the operation after validating an LLM proposal.

| Node | Reads | Writes | How the writes happen |
|---|---|---|---|
| `load_corpus` (with a seed) | R1, R16 | W29 (seed import), W27 | code |
| `summarize`, `get_minibatches`, `open_code_minibatch` | — | — | no taxonomy access |
| `generate_taxonomy` | — (open codes, feedback) | W17, W25, W27 | via node, from the LLM's full taxonomy |
| `update_taxonomy` (tools mode) | R13 (prompt), R11, R17, R6 | W1–W14, W27 | **directly**: the Taxonomist calls the operations as tools |
| `update_taxonomy` (rewrite, rewrite_restore) | R13 | W17, W26, W25, W27 | via node |
| `evaluate_taxonomy` (loop) | R1, R13 (judge), R12, R20 | — | read-only |
| `check_saturation` | R14, R13 | — (writes feedback, not the taxonomy) | read-only |
| `review_taxonomy` | as `update_taxonomy` | as `update_taxonomy` | as `update_taxonomy` |
| `consolidate_values` | R12, R9, R7, R13 | W25, W21, W20, W18, W19, W23 and W15 (repair, off by default), W22 (recoding), W27 | via node; the repair applies W3, W6, W10, W13, W15 through the editor |
| `select_dimensions` | R12 (evidence rank, exclusivity), R13, R7 | W28 | via node |
| `label_documents` | R1 (selected), R13 | — (labels documents, not the taxonomy) | read-only |
| `aggregate_new_values` (test mode) | R1, R11 | W1, W2, W27 | via node |
| `evaluate_taxonomy_final` | R1, R13, R12 | — | read-only |
| decision focus (variant, `benchmark/focus_variant.py`) | R12, R13 | W24, W11, W25 | via node, through the editor |

### Who uses which operation: agents and other actors

| Actor | Kind | Reads | Writes | Notes |
|---|---|---|---|---|
| Taxonomist (generate, update) | pipeline LLM | rendered view (R13) in its prompt | W1–W14 as tools (tools mode); W17 (generate, rewrite) | the only LLM that calls write operations itself |
| Reviewer (`review_taxonomy`) | pipeline LLM | R13 | as the Taxonomist | |
| Saturation critic | pipeline LLM | R14, R13 | — | feedback only |
| Critic / judge (evaluation) | pipeline LLM | R13 (judge view), R12 | — | scores only |
| Dimension-merge LLM | pipeline LLM | R13 | proposes → W21 | |
| Value-merge LLM (consolidation) | pipeline LLM | R4, R8 | proposes → W20 | |
| Selection LLM | pipeline LLM | R13, R12 | proposes → W28 | |
| Recoding LLM | pipeline LLM | R4, R9, value combinations (R12) | proposes → W22 | validated before applying |
| Exclusivity-repair LLM | pipeline LLM | R12, R4 | proposes → W3, W6, W10, W13, W15, W23 | off by default; `extract` adds a `refines` relation |
| Labeler | pipeline LLM | R1 (selected), R13 | — | labels documents |
| Focus LLM (variant) | pipeline LLM | R13 | proposes → W24, W11 | |
| Wiki builder (`ddspace wiki build`) | code + LLM extras | R1, R13 (wiki, graph), R14, R18 | — | read-only; writes its own files |
| Coding agent via `ddspace query` / `point` | external agent | R2–R10, R18, R19 | — | today |
| Coding agent via `ddspace edit` / tools (U7) | external agent | as above + R16, R15 | W1–W16, W29 | new; validated as for the Taxonomist; `actor: agent` |
| Human via `ddspace` | person | as above | W1–W16 (`edit`), W29 (`import`), feedback to a re-mine | new commands in U7; `actor: human` |
| Benchmarks (`benchmark/*.py`) | scripts | R1, R12, R18 | replay applies W18–W28 through the nodes | the equivalence gate (U0) |

The tables show that **all writes reduce to 29 operations**, and that only the Taxonomist, the Reviewer and the
repair step reach write operations directly. Everything else proposes and lets code apply. U3 implements R1–R19
and W1–W16 (plus W27); U5 adds W17–W26 (and R20, which reuses W18 on a copy) one pass at a time; U7 exposes R2–R19, W1–W16 and W29 to people and
agents.

## Implementation units

| Unit | What | Files | Risk |
|---|---|---|---|
| **U1** | Model and lossless conversion. `Taxonomy.from_dicts`/`to_dicts`, `from_run_file`/`to_run_file`, `validate()` returning problems (duplicate ids, a value whose `dimension_id` disagrees with its dimension, dangling relation targets, statuses outside `DecisionStatus`, a stance whose doc is not in `supporting_doc_ids`). A round-trip test over all committed run files. **Nothing in the pipeline changes.** | new `model/{taxonomy,validate}.py`; tests | Low |
| **U2** | Stable uids (KTD3): deterministic for files without them, assigned on creation, written as an extra key. Name-based matching in `wiki_build.diff` becomes uid-based, falling back to names. | model; `wiki_build.diff` | Low–medium |
| **U3** | Operations and log. Move the 14 editor operations onto the model (`apply(taxonomy, op)`); `TaxonomyEditor` becomes a thin LLM-facing adapter, with the same tool schemas, error messages and aliases. `Operation` records gain `actor`, `uid`s and a timestamp. | `taxonomy_editor.py`, `tool_update.py`, new `model/ops.py` | Medium |
| **U4** | Store protocol and `FileStore` (today's layout). `pipeline_cli` saves through it; `load_seed_taxonomy` and `delvedspace.runs.find_taxonomy` load through it. | `pipeline_cli.py`, `utils.py`, `delvedspace/runs.py` | Low |
| **U5** | Bulk operations for the post-mining passes, **one pass per PR**, each behind the equivalence gate: evidence linking → value consolidation → dimension merging → value recoding → exclusivity repair → `restore_dropped_values` / `carry_over_evidence` / `ensure_unique_ids` | `nodes/*.py`, `utils.py`, `relations.py` | **High** (paper numbers) |
| **U6** | Rewrites as diffs (KTD5): `generate_taxonomy` and `rewrite`/`rewrite_restore` updates and reviews produce operation logs. | `nodes/taxonomy_{generator,updater,reviewer}.py` | Medium |
| **U7** | External authoring and import. A published JSON Schema (from the models) and a friendlier YAML form; `ddspace import FILE` (validate, report problems, write a run); `ddspace edit` (the operations as subcommands); the operations as agent tools (MCP or CLI) with the same validation. | new `delvedspace/{importer,edit}.py`; docs | Medium |
| **U8** | Optional: model objects in the LangGraph state, a second store backend (SQLite), operation-log storage (event sourcing). Each only when there is a user for it. | `state.py`, `model/store_*.py` | Medium |

## Change impact analysis

Counts come from two AST scans of `src/` and `benchmark/` (scripts kept in the session scratchpad): in-place
writes to taxonomy keys (assignments, `del`, `append`/`extend`/`pop`/`setdefault`/... on `d["values"]` and
similar), and dict literals that build a value, dimension or relation, including `{**v, ...}` copies. They are
lower bounds: writes through local aliases (`vals = d["values"]; vals.append(...)`) are not counted.

### Code that changes the taxonomy (producers)

| Module | Writes | Builds | Functions | Unit | Change | Paper numbers at risk? |
|---|---|---|---|---|---|---|
| `taxonomy_editor.py` | 22 | 5 | `_place`, `_relabel_value`, `_rename_dimension`, `_split_dimension`, `_merge_dimensions`, `_add_value`, `_add_relation`, `_remove_relation`, `result` | U3 | Logic moves to `model/ops.py`; the editor keeps tool schemas, aliases and messages | Yes (tools mode); identical logic, same tests |
| `utils.py` | 16 | 1 | `restore_dropped_values`, `ensure_unique_ids`, `carry_over_evidence`, `_prune_relations`; read-only views `format_taxonomy`, `taxonomy_prompt_view` | U5 | The three mutators become operations; the views read the model | Yes (`rewrite_restore`, uid fixes) |
| `nodes/value_recoding.py` | 3 | 7 | `apply`, `recode` | U5 | `replace_values` bulk op; validation stays in the node | Yes (on by default) |
| `nodes/exclusivity_repair.py` | 9 | 5 | `merge_candidates`, `_apply_round` (already uses the editor) | U5 | `merge_candidates` becomes the stance-union merge op | Low (off by default) |
| `nodes/evidence_linker.py` | 8 | 0 | `link_evidence`, `drop_unsupported_values` | U5 | `link_evidence` bulk op (adds docs, stances, counts, dimension evidence); `remove_unsupported` | **Yes**: every value's evidence |
| `nodes/value_consolidator.py` | 5 | 3 | `consolidate_values`, `_consolidate_values`, `_merge_group` | U5 | `consolidate_group` bulk op (stance union, mixed status) | **Yes**: value counts, statuses |
| `nodes/dimension_merger.py` | 4 | 1 | `merge_groups` | U5 | `merge_dimensions` (exists) with relation rewiring | Yes |
| `nodes/value_aggregator.py` | 1 | 3 | `aggregate_new_values`, `_collect_candidates` | U5 | `add_value` ops (test mode) | Low (test mode) |
| `nodes/decision_focus.py` | 2 | 2 | `recompute_evidence`, `_dimension_summary` | U5 | Recompute as a model method | Low (variant) |
| `relations.py` | 2 | 2 | `clean_relations` | U3 | Becomes `validate()`/normalization on the model | Yes (relation counts); pure, so easy to check |
| `nodes/taxonomy_{generator,updater,reviewer}.py` | 0 | 0 | whole-taxonomy LLM output | U6 | Diff → ops | No (same taxonomy, plus a log) |
| `nodes/dimension_selector.py` | 0 | 0 | builds `selected_clusters`, `apply_cap` | U5 | Selection as a view (`taxonomy.select(ids)`), no copy edits | Yes (cap); pure |
| `nodes/doc_labeler.py`, `saturation_checker.py`, `taxonomy_evaluator.py` | 0 | 0 | read `clusters[-1]` | U1 | Optionally read through the model | No |

The scans find 84 in-place writes and 45 constructions in 20 modules. 12 writes and about 15 constructions are in
read-side code (`wiki/`, `evaluation/`, `visualization.py`, `delvedspace/point.py`, a display name in
`pipeline_cli`): they edit copies made for display or judging, and need no change. The rest, about 72 writes and 30
constructions in the modules above, change the taxonomy. The
**semantic hot spots** are
evidence linking, consolidation and recoding: they decide evidence, statuses and value counts, which feed every
reported metric.

### Code that reads the taxonomy (consumers)

| Consumer | Reads | Impact |
|---|---|---|
| `pipeline_cli.run` (writer), `load_seed_taxonomy`, `resolve_seed_view` | run file | U4: through `FileStore`; format unchanged (KTD2) |
| `wiki/model.py`, `wiki/query.py`, `wiki/okf.py` (wiki, `graph.json`, OKF) | run file (`view_dimensions`) | None at first; `graph.json` may gain `uid` (schema version bump only if exposed) |
| `delvedspace/{runs,wiki_build,check,point}.py` | run file, `raw/graph.json` | U2: diff by uid; U4: load via store |
| `evaluation/{runner,gt_match,exclusivity,design_points,stage_funnel,quality_probe}.py` | dicts (`selected_clusters`, iterations) | None; they keep receiving `to_dicts()` |
| `html_report.py`, `report_renderer.py`, `visualization.py` | state and run file | None |
| `routing/should_*.py` | `len(state.clusters)` | None (KTD1 keeps snapshots) |
| `benchmark/*.py` (8 scripts: `replay_consolidation`, `export_wiki`, `selection_variant`, `focus_variant`, `design_points`, `describe_design_points`, `quality_probe`, `stage_funnel`) | run file, dicts | None while KTD2 holds; `replay_consolidation` becomes the equivalence harness |

### Interfaces and formats

| Interface | Change | Compatibility |
|---|---|---|
| Run file JSON | Optional `uid` on dimensions and values (U2); richer `operation_log` records (U3) | Old files load (uids derived); old readers ignore the extra keys |
| `raw/graph.json` (wiki) | Optional `uid` per node | `schema_version` stays 1 unless queries use it |
| `--taxonomy` seed / `ddspace update` | Validated through `Taxonomy.validate()` | Stricter: a malformed seed that used to pass is reported (warnings first, errors for real breakage) |
| LLM tool schemas (tools mode) | None | Same names, args and messages; prompts unchanged |
| `ddspace` commands | New `import`, `edit` (U7) | Additive |
| Configuration | Maybe `storage:` (backend, path) in U4/U8 | Defaults reproduce today's behavior |

### Tests

- **Dict fixtures.** 16 of 62 unit test files build taxonomy dicts directly (54 `supporting_doc_ids`
  occurrences). With KTD1 and KTD2 they keep working, so no mass rewrite is needed. New code is tested against
  the model.
- **New tests:**
  - round trip on all committed run files (U1);
  - `validate()` cases;
  - every operation: the 14 atomic ones, the bulk ones, alias behavior, uid preservation;
  - `FileStore` load and save;
  - the importer (valid file, each class of problem).
- **Existing tests that must pass unchanged:** `test_taxonomy_editor*`, `test_tool_update*`,
  `test_value_recoding.py`, `test_value_exclusivity.py`, the consolidation and evidence linking tests, and all
  `ddspace` tests. They are the behavioral spec of what moves.

### Results (paper) and runs

- No mining is repeated. The **equivalence gate** for U3, U5 and U6 replays saved runs before and after each
  change and requires identical output:
  - `benchmark/replay_consolidation.py` on C1 (`20261002_185546`) and C2 (`20261002_211657`), whose open codes
    and documents are local but not committed (copyright), and on the C3 runs of 2026-10-15;
  - plus `--match-gt` with the independent matcher.
- **LLM non-determinism.** Consolidation, recoding and merging call the LLM, so two replays differ even without a
  code change. The gate therefore needs a **record/replay cache for LLM calls** (U0, below): record the responses
  once, then replay them with the old and the new code. Without it, equivalence is only statistical and the gate
  is weak.
- Paper numbers are frozen for the submission, and U5 lands after it.

### Documentation

- `CONCEPTS.md`: a "Taxonomy model", "Operation" and "Store" entries.
- `USAGE.md`: `ddspace import`/`edit`.
- The `AGENTS.md` guide: authoring via tools.
- `benchmark/README.md`: a change-log entry per unit that touches the pipeline.
- A `docs/solutions/` entry after U5.

### Performance

- The model is small: at most a few hundred dimensions and a few thousand values.
- Pydantic validation and conversion at node boundaries cost milliseconds, against LLM calls of seconds.
- The deterministic uid derivation hashes labels and is linear.

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| A refactored pass changes results silently | Medium | High (paper claims) | LLM record/replay gate (U0), one pass per PR, identical-output requirement, independent matcher |
| Round trip loses or reorders data | Low | High | `extra="allow"`, the round-trip test over 44 run files, semantic JSON equality |
| Ids change meaning (recoding renumbers) and history breaks | Medium | Medium | `uid` (KTD3); display ids remain presentation |
| Bulk ops become a "do anything" escape hatch | Medium | Medium | Each bulk op has its own validation and invariants, and is logged with its inputs |
| A stricter seed validation rejects users' files | Low | Low | Warnings first, errors only for broken references; `--no-validate` |
| Scope creep (event sourcing, DB backends) | Medium | Medium | U8 only on demand; `FileStore` is the default |
| Work collides with the submission | High if started now | High | Only U1 (and U0) before 2026-10-23; the rest after |

## Sequencing

0. **U0: an LLM record/replay cache** for `load_chat_model` (keyed by model and prompt hash; record, replay and
   off modes). It is useful on its own: free reruns of benchmarks, and deterministic replays. It is a
   prerequisite for gating U3, U5 and U6.
1. **U1, then U2:** additive; nothing in the pipeline changes. U1 can be done before the submission.
2. **U4, then U3:** storage and atomic operations; the tools-mode tests are the spec.
3. **U5,** pass by pass, each with the gate.
4. **U6, then U7:** a log for every mode, then import, edit and agent tools.
5. **U8** on demand.

## Out of scope

- Changing what a dimension or value means, or any mining algorithm.
- A database backend before there is a user for it.
- Real-time multi-user editing.

## Open questions

1. Should the import format be JSON only (the run-file subset), or also a hand-friendly YAML form?
2. Should agents edit through `ddspace edit …` CLI commands (simple, same permission model) or an MCP server
   (richer, one more moving part)?
3. Should human and agent edits made after mining be marked in the wiki (for example "edited by a person"), and
   should `ddspace update` keep them when it re-mines?
4. Should `uid` appear in `graph.json` and `ddspace query` output, or stay internal?
