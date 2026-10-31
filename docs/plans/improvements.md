---
title: "Improvements: planned developments for Delve and ddspace"
type: index
status: living document (created 2026-10-31); nothing here is scheduled yet
date: 2026-10-31
---

# Improvements

Five planned developments, recorded after the SANER and CAIN submissions. Each has its own plan. This page
gives their status, how they depend on each other, and a suggested order. Update it when a plan changes status.

## The five improvements

| # | Improvement | Plan | Feasibility | Effort | Status |
|---|---|---|---|---|---|
| 1 | **Taxonomy data layer.** The design space as a data structure with a defined interface (model, operations, store), so that the LangGraph pipeline is one construction procedure among others | [2026-10-15-refactor-taxonomy-data-layer-plan.md](2026-10-15-refactor-taxonomy-data-layer-plan.md) (refreshed 2026-10-31) | High; already designed | U0–U4: about 1–2 weeks; U5 (moving the post-mining passes) is the risky part | `ddspace import` built (part of U7); U0–U6 not started |
| 2 | **Forces and trade-offs (2a).** Forces, impacts (`++` to `--`), forces per decision and typed option links, as in the C1/C2 expert models; imported, shown in the wiki, `query` and `point`. Not mined yet | [2026-10-31-feat-forces-and-trade-offs-plan.md](2026-10-31-feat-forces-and-trade-offs-plan.md) | High for 2a; mining (2b) and evaluation (2c) are research, deferred | about 1 week | Proposed |
| 3 | **Wiki radial layout and domain node.** A force / radial switch in the graph view (rings from the domain outwards) and a central domain node, also the tree's root. Label from the workspace name, overridable with `taxonomy.domain` | [2026-10-31-feat-wiki-radial-layout-domain-node-plan.md](2026-10-31-feat-wiki-radial-layout-domain-node-plan.md) | High; small and independent | 1–2 days | Proposed |
| 4 | **Model profiles.** Several providers and models in one run: named profiles, per-node overrides, per-model settings, capability checks, cost per model | [2026-10-31-feat-model-profiles-plan.md](2026-10-31-feat-model-profiles-plan.md) | High; partly there (any LangChain provider, three roles) | about 1 week | Proposed |
| 5 | **Multi-persona coding.** Several analyst personas, each with the same or a different LLM, in open, axial and selective coding, closer to a grounded-theory team | [../DESIGN_SPACE_ROADMAP.md](../DESIGN_SPACE_ROADMAP.md) (refreshed 2026-10-31; units M0–M4) | Medium; must first pass the Phase 0 gate (persona differences larger than rerun noise) | M0: runs only; M1: days; M2–M3: weeks | Phase 0 not run |
| 6 | **Hybrid construction (extend).** An expert supplies the dimensions and some values; mining adds values with evidence. A constrained seeded train mode: `taxonomy.freeze_dimensions` plus protected expert values (`origin: expert`); `ddspace update --extend`. Not a case of test mode, which labels each passage once and skips open coding, stances and evidence for the seed | Section 4 of the Designing 2027 paper plan (`docs/paper/designing2027/DESIGNING2027_PAPER_PLAN.md`, local); split into a feature plan if it outlives the paper | High; seeded train and test mode exist | 2–3 days | Planned for the Designing 2027 paper (due 2026-11-13) |

## Scope: the approach and the tool alike

Every improvement applies to both:

- the **DelveDSpace approach**: the mining pipeline in `src/taxonomy_generator`, configured by `config.yaml`
  and run with `python -m taxonomy_generator` and the benchmark scripts;
- the **ddspace tool**: `src/delvedspace`, configured by a workspace's `ddspace.yaml`.

`ddspace.yaml` uses the pipeline's configuration schema plus its `workspace:` and `wiki:` blocks. A setting
therefore goes into the shared schema whenever both sides need it, and the tool exposes it through its commands.

| # | Approach (pipeline) | Tool (ddspace) |
|---|---|---|
| 1 | LangGraph nodes become producers of validated operations; the run file goes through the store | `ddspace import` validates; `ddspace edit` and agent tools emit the same operations |
| 2 | Forces survive seeded runs (`--taxonomy`) and the editor's operations; the pipeline's report and wiki export show them; `taxonomy_to_gt` exports them | `ddspace import` keeps them; the wiki, `query` and `point` show them |
| 3 | The pipeline's wiki export (`benchmark/export_wiki.py`) gets the same views and label | `ddspace wiki build` gets the views; the label is `taxonomy.domain` in `ddspace.yaml` (same key in `config.yaml`) |
| 4 | `models.profiles` and `models.nodes` in `config.yaml`; usage and cost per model in the run file | The same keys in `ddspace.yaml`; `ask` and `point` take a profile; `check` shows each node's model |
| 5 | `personas:` in `config.yaml`; per-persona open coding, drafts and selection | The same key in `ddspace.yaml` (commented in the template); `check` lists personas; wiki pages show persona provenance |
| 6 | `taxonomy.freeze_dimensions` in `config.yaml`; seeds (`--taxonomy`) mark their values `origin: expert`; the editor, linker and consolidation protect them | `ddspace update --extend` after `ddspace import --kind decision-model`; the wiki marks expert and mined values |

## Dependencies

```
3  Wiki radial + domain node            independent
4  Model profiles  ──required──▶  5  Multi-persona (personas on different LLMs; M0's model contrast)
1  Data layer U1   ──preferred──▶ 2  Forces (model classes and validation instead of more dict keys)
1  Data layer U3   ──required──▶  5  M2 reconciliation (operations with an actor; diff and merge of drafts)
1  Data layer U0   ◀──shared──▶   4  (the record/replay cache keys on the resolved model and profile)
2  Forces          ──adds to──▶   3  (a ring for forces, hidden by default)
2  Forces          ──adds to──▶   DESIGN_SPACE_ROADMAP Phase 4 (value-level requires/excludes in `point`)
```

- **Hard dependencies** are only two: personas need model profiles to use different LLMs, and persona
  reconciliation needs the data layer's operations.
- **The equivalence gate** (data-layer U0, replay with recorded LLM answers) protects every change that touches
  the pipeline: the data layer itself, model profiles and personas. With default settings each must reproduce
  today's output exactly.
- **The CAIN study** holds forces out of the agent's view and scores with them. The forces plan pins
  `--no-forces` in the study's workspace builder, with a guard test.

## Suggested order

| Step | Work | Why here |
|---|---|---|
| 1 | **3** Wiki radial layout and domain node | A quick win, with no dependencies and nothing at risk |
| 2 | **1 U0** record/replay cache, then **4** model profiles | The cache makes every later pipeline change checkable. Profiles are low risk and unblock personas. |
| 3 | **1 U1–U4** model, stable ids, store, atomic operations | Additive, behind the gate. U1 unblocks forces. |
| 4 | **5 M0** the Phase 0 measurement | Runs only. It can happen any time after profiles; it decides whether M1–M3 are worth building. |
| 5 | **2** forces and trade-offs (2a) | On the model layer from step 3 |
| 6 | **5 M1, then M2–M4** if the gate passes | M2 needs U3 from step 3 |
| 7 | **1 U5–U7** the remaining data-layer units, one pipeline pass per PR | The risky part, each pass behind the equivalence gate |

## Conventions for these plans

- Each plan lists its current state with file references, key technical decisions (KTDs), implementation units,
  verification, risks and open questions.
- Defaults reproduce today's behaviour: new settings are optional, and old configs, run files and wikis keep
  working.
- Paper artifacts are frozen on the `artifact-paper` and `artifact-tool` branches. Main may change freely, but
  the C1–C3 numbers remain the reference behaviour for the equivalence gate.
