# Paper to-do before the freeze (SANER 2027)

Status as of 2026-10-07. Deadlines: abstract 2026-10-19, paper 2026-10-23. The full plan, with item codes, is
`docs/paper/SANER2027_PAPER_PLAN.md` (§8.6b); this page restates the open items in plain terms.

The paper's claim is that **Delve finds the design decisions that experts found**. Each item below supports
one part of that claim.

**Freeze:** from a fixed date (planned 10-09/10, likely to slip one or two days) code and settings stop
changing, and the main runs start (3 seeds each). Anything that changes how Delve runs or how runs are
recorded must land before it.

| # | Item | Plan code | Who | Before freeze? | Status |
|---|---|---|---|---|---|
| 1 | Human check of the judge | A6 | Co-authors (labeling) + me (sheet) | Before the numbers count | Open |
| 2 | Baselines: one long prompt; model without the corpus | L1, L5 | Me | Yes | Open |
| 3 | Ablation switches: no open coding; no critic feedback | P12 | Me | Yes | Open (rewrite vs. tools is done) |
| 4 | Run record (provenance) | P13 | Me | Yes | Open |
| 5 | Statistics and results tables | A3, A4 | Me | Can follow | Open |
| 6 | Third case study (Git at scale) | B6, B7, B9 | Me (B6, drafts); authors (review) | Corpus yes; runs after | Drafts done; author review open |

## 1. Is the scoring trustworthy? Human check of the judge (A6)

- **What:** an LLM decides whether a Delve option matches an expert option. Today it is the same model that
  generated the taxonomy, so it grades its own work, and the judge's choice moved C2's score by about 0.2.
  Two co-authors hand-label a sample of pairs ("same option or not?"). We measure their agreement with each
  other (κ) and with the LLM judge.
- **If missing:** every reported number is open to "your judge is lenient". This is the weakest point.
- **Who:** co-authors label; I prepare the sheet (`benchmark/HUMAN_CHECKS.md`).
- [ ] Labeling sheet prepared
- [ ] Two authors label
- [ ] κ and judge agreement computed

## 2. Compared to what? Baselines (L1, L5)

- **L1, "just ask the LLM":** the whole corpus in one long prompt, same model, asking for the design space.
  If Delve does not beat it, the multi-step pipeline is not justified.
- **L5, "does the model already know?":** ask for the design space with no corpus. The C1/C2 papers are
  published, so the model may have memorized them. A good score here means our numbers partly reflect
  memory.
- **If missing:** no comparison in the paper, which usually means rejection.
- **Who:** me, about 0.75 day plus runs.
- [ ] L5 probe
- [ ] L1 baseline
- [ ] Both scored with the matcher

## 3. Which parts of Delve matter? Ablations (P12)

- **What:** run Delve with one part off: (a) no open-coding step, (b) no critic feedback in the loop,
  (c) rewrite vs. tools. (c) is done through `taxonomy.edit_mode`; (a) and (b) need on/off switches.
- **If missing:** the agentic-roles story (RQ3) becomes a description instead of a result.
- **Who:** me, about 0.5 day plus runs.
- [ ] Switch: no open coding
- [ ] Switch: no critic feedback

## 4. Can someone reproduce a run? Run record (P13)

- **What:** each run saves its config, code version, models (including the judge), a fingerprint of the
  prompts, the seed and token counts.
- **If missing:** weak replication package (SANER weighs open science). It must exist before the main runs,
  or those runs cannot be traced.
- **Who:** me, about 0.25 day.
- [ ] Provenance block in every saved run

## 5. Are differences real or noise? Statistics (A3, A4)

- **What:** a script that turns runs into the results tables: averages over 3 seeds, confidence intervals,
  and paired differences with effect sizes ("Delve beats L1 by X").
- **If missing:** tables by hand, no significance claims.
- **Who:** me, about 1 day. It only reads results, so it can follow the freeze.
- [ ] Harness and tables

## 6. Third case study: Git at scale (C3)

There is no expert answer key, so this case is mostly qualitative. It shows the design space the way Shaw
did: several organizations (GitHub, Google, Microsoft, Cursor) as points in it.

- **B6, corpus (me):** passages from the Cursor article and its official background sources, prepared like
  C1/C2 (C3-raw), plus the existing 16 curated documents as a sensitivity check (C3-curated).
- **B7, passage → system map (authors):** which passages describe which system. Needed to place each system
  in the design space.
- **B9, silver trade-off list (authors):** the trade-offs the article states, with the systems and quality
  attributes involved.
- B7 and B9 must be written **before** anyone sees Delve's C3 output.
- **Current approach:** I draft B7 and B9 as provisional versions from the sources only (not from any Delve
  output), and the authors review them. The paper uses my unreviewed draft as primary and the reviewed
  version as a sensitivity check (decision 2026-10-08).
- **Where:** `benchmark/c3-git-at-scale/` (README with status, bias guard, review checklist and log);
  configs in `examples/c3-git-at-scale/`. Plan: `docs/plans/2026-10-07-2346-feat-c3-git-at-scale-corpus-and-silver-lists-plan.md`.
- **Decided 2026-10-08 (before any C3 run):** `min_dimension_sources: 1` for C3-raw (2 for curated);
  `batch_size: 8` for C3.
- **After the freeze:** C3 runs, the system × dimension matrix (A9), the design-point check (E13).
- **If missing:** two cases only; acceptable but weaker on generality.
- [x] B6 C3-raw corpus (48 passages from 5 sources)
- [x] B6 C3-curated corpus (16 documents with ids) and configs
- [x] B7 draft (agent): 48 passages + 16 curated documents mapped
- [x] B9 draft (agent): 20 stated trade-offs
- [ ] Design-point check (E13), framed as *coherence of the design space*. Exploring novel combinations is
  an intended contribution: novel points get a workable / conditional / unfeasible verdict, not a grounding
  pass/fail.
  - [x] Sampler (A12): `benchmark/design_points.py`
  - [ ] Judge (A13)
  - [ ] Human rating of about 30 points
- [ ] Usability task: 2–3 raters use the taxonomy on a scenario from the article. This, not the judged sample,
  supports a usability claim.
- [ ] Authors review B7 and B9 (checklist and log in `benchmark/c3-git-at-scale/README.md`)
- [ ] Two authors agree on the C3 use case (both C3 configs)

## Deferred (not before the paper)

- Wiki/graph export of a taxonomy: decided plan in `docs/DESIGN_SPACE_EXPLORATION.md` §13 (llmwiki-style
  wiki + graph site for a meeting demo, with a design-points page; paper figures: overview, C3 system ×
  dimension matrix, C1/C2 ground-truth comparison). Own feature branch, before the paper figures are needed.
- Decision-focus pass (bundled decisions): `docs/plans/2026-10-08-1500-feat-decision-focus-pass-plan.md`;
  own feature branch, before the C1/C2/C3 re-runs. It also covers **dimension granularity**: Delve mines more,
  finer dimensions than the experts (C1 30 vs 10/28, C2 19 vs 7, C3 22). The wiki's "core dimensions" filter
  is a presentation aid only, not a fix.
- BERTopic baseline (L2), drivers and relations as matched elements, personas, theoretical sampling: future
  work (plan §8.6b, "Scope for the paper").
