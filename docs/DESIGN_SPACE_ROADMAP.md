---
title: Design Space Roadmap — multi-persona GT + Shaw-faithful exploration
description: A refined, phased implementation plan for making Delve approximate Mary Shaw's design-space notion more closely (flat/1-level for now), by simulating multiple analyst personas across open, axial, and selective coding, and by adding a distinct "unoccupied points" exploration capability.
generated: 2026-08-21
supersedes: >-
  The multi-persona bullet in docs/NEW_IDEAS.md (options A/B only) is refined and extended here to
  cover selective coding too, per direct request. docs/GT_DESIGN_SPACE_ASSESSMENT.md's enhancements
  E1-E6 remain valid and are cross-referenced, not repeated.
---

# Design Space Roadmap: Multi-Persona Grounded Theory + Shaw-Faithful Exploration

## What changed since the last assessment

Two decisions sharpen the plan in `docs/GT_DESIGN_SPACE_ASSESSMENT.md` into something buildable:

1. **The mined design space should be treated as generative, not just descriptive.** Once a dimension/value
   structure exists, it should let a designer explore *unoccupied points* — combinations of values across
   dimensions that no document in the corpus actually exhibits — not only describe what's already there.
   This is Shaw's own framing (unoccupied points are "an opportunity for new products," not noise), and it
   needs to become a real, separate pipeline capability, not a footnote.
2. **Multi-persona simulation should span open, axial, *and* selective coding**, not just the first two.
   That means `select_dimensions` — currently a single-voice relevance filter — also gets a persona
   treatment, which conveniently gives Delve a real path back toward classic selective coding's core-category
   integration (see Phase 3).

Two new bodies of literature ground this refinement, beyond what the previous assessment covered:

- **Nelson (2020), "Computational Grounded Theory: A Methodological Framework"** ([PDF](https://hengxyz.github.io/resources/nelson-computational-grounded-theory-rotated.pdf),
  [SMR](https://journals.sagepub.com/doi/abs/10.1177/0049124117729703)) — the foundational CGT paper.
  Its three-stage architecture (**pattern detection** → **pattern refinement** → **pattern confirmation**)
  has one principle Delve doesn't yet fully apply: a pattern found by one computational method should be
  confirmed by an **independently different** method before being trusted, not just re-checked by more of
  the same technique. Delve already does this at the *value* level — `value_consolidator.py` merges by
  embedding distance (one method) and adjudicates borderline cases by LLM judgment (a genuinely different
  method) — but not yet at the *dimension* or *selective-coding* level. This roadmap generalizes that
  existing pattern upward.
- **"LLM-enhanced computational grounded theory and the triadic dynamics of human-AI-society interaction"**
  ([Springer, *Theory and Society*, 2026](https://link.springer.com/article/10.1007/s11186-026-09734-7)) —
  directly on point. It triangulates **LLM-assisted coding**, **independent human open-axial-selective
  coding by two separate annotators**, and **corpus-scale computational validation** (topic modeling
  checking whether the sample-derived codebook explains the full corpus), and treats LLMs explicitly as
  "analytic instruments within a human-led workflow," not autonomous theorists. Two things from it matter
  most here: its explicit **saturation-by-round-over-round-diff** test ("additional iterations yield only
  marginal changes to the thematic structure" — a cleaner operationalization than Delve's current
  concept-coverage-only saturation check), and its blunt warning about **prompt sensitivity**: "changes in
  prompt formulation can generate differences in topic structure that reflect analytic instrumentation
  rather than variation in the data itself." That warning is the single biggest risk to the multi-persona
  plan below, and it gets an explicit safeguard (Phase 0).
- The [Computational Grounded Theory topic
  overview](https://www.emergentmind.com/topics/computational-grounded-theory) the request referenced
  functions mainly as an index into the above two papers and related work (e.g. [Carlsen & Ralund,
  "Computational grounded theory revisited: From computer-led to computer-assisted text
  analysis"](https://www.semanticscholar.org/paper/Computational-grounded-theory-revisited:-From-to-Carlsen-Ralund/7878f57a5483ab53fd92d25f275194a41856fc26)),
  which echoes the same computer-assisted-not-computer-led framing.

## Design principle carried through every phase

**Persona disagreement must be shown to be a real perspective difference, not prompt-formulation noise,
before it's trusted as triangulation.** The 2026 paper's prompt-sensitivity warning is specific and
falsifiable: if two runs of the *same* persona (identical system prompt, different temperature or document
order) disagree about as much as two *different* personas do, the personas aren't adding perspective — they're
adding noise dressed up as perspective. Phase 0 below builds this as an actual measurement, not a caveat in
prose, and every later phase's rollout gate references it.

---

## Phase 0 — Measure before building (cheap, no graph changes)

Goal: decide whether multi-persona coding is worth its cost *on your actual corpora* before touching
`graph.py`.

1. Pick 2–3 personas grounded in a real `use_case` (not cosmetic role-play) for one existing example
   corpus (`campus-bike` or `pharmacy-food`).
2. Run the **existing, unmodified** pipeline once per persona (persona folded into `use_case` text), plus
   twice more with the *same* single persona and a different `random_seed` — this gives a same-persona
   noise-floor baseline for free, no code changes.
3. Feed all N+2 saved taxonomy JSONs into `evaluation/consistency.py`'s `compare_taxonomies` (already
   N-way, already unwired into the CLI but directly importable) and compare the **agreement score** between
   the two same-persona reruns against the agreement score across different personas.
4. **Gate**: if cross-persona agreement is *not* meaningfully lower than same-persona-rerun agreement,
   stop here — the personas you picked aren't distinguishing themselves from noise, and the fix is better
   personas, not more architecture. If it is meaningfully lower (more disagreement across personas than
   across reruns of one persona), that's the signal multi-persona triangulation has something real to
   contribute, and Phases 1–3 are justified.

This phase costs N+2 full pipeline runs and zero new code — it's the same "Option D" already logged in
`docs/NEW_IDEAS.md`, now given a specific, falsifiable pass/fail criterion instead of an open-ended
experiment.

---

## Phase 1 — Multi-persona open coding

Unchanged from the `docs/NEW_IDEAS.md` entry: `config.yaml` gets a `personas:` list (id, lens
description, optional per-persona model override); `open_coding.md` gets a `{persona}` slot (empty by
default, non-breaking); `_setup_open_coding_chain` builds one chain per persona; `open_code_minibatch`
fans out per document × persona (it already does `asyncio.gather` per document, so this is a local
change); `OpenCode` gets an optional `persona` field for provenance. Cost multiplies by N at the
open-coding stage; consolidation load on `value_consolidator.py` increases since different personas will
often name the same decision differently.

**New for this roadmap**: tag every `OpenCode.persona` and keep it through to the `Value.supporting_doc_ids`
provenance so Phase 4's exploration step can (optionally) report which personas' reading a given value
rests on — directly the "tag by source" precedent from Shaw's own worked example (her tree tags every
value with which of her three sources — a team, the prompt, or a commercial product — produced it).

---

## Phase 2 — Multi-persona axial coding, with real reconciliation

Unchanged core design from `docs/NEW_IDEAS.md`: `generate_taxonomy`/`update_taxonomy` run once per
persona over the same open codes; persona drafts land in a new **per-iteration-only** state field (not
directly in `clusters`, which is a whole-run `operator.add` accumulator every downstream node reads via
`clusters[-1]`); a new reconciliation node merges the N drafts into one `List[Cluster]`, appended once to
`clusters`; inserted *before* `check_saturation` so every downstream node (`check_saturation`,
`review_taxonomy`, `consolidate_values`, `select_dimensions`) needs no changes.

**Sharper reconciliation logic, per Nelson's confirmation principle**: extend `compare_taxonomies`'s
embed-then-align approach so that a dimension recurring across a *majority* of personas' drafts is kept
outright (persona agreement *is* one form of confirmation), while a dimension proposed by only one
persona is **not automatically dropped** — it gets routed to a second, independently-different check
before being kept or discarded: does it also show up as a coherent cluster in a plain embedding pass over
the same minibatch's open-code labels (no LLM judgment involved)? This mirrors Nelson's pattern-confirmation
move directly — the persona vote is one method (interpretive/LLM), the embedding-cohesion check is a
genuinely different one (distributional/statistical) — rather than asking a second LLM call to bless a
first LLM call's idiosyncratic finding, which would not actually be independent confirmation.

**Sharper saturation, borrowing the 2026 paper's round-over-round diff**: alongside the existing
concept-coverage check in `check_saturation`, add a second signal — the size of the *edit* between this
iteration's merged taxonomy and the previous one (dimensions added/removed/renamed, values added, relations
added) — and treat saturation as reached only when *both* concept-coverage saturates *and* the round-over-round
edit falls below a small threshold for the configured streak. This directly implements
`docs/GT_DESIGN_SPACE_ASSESSMENT.md`'s enhancement E4 (saturation should cover relationships, not just
concepts) using a concrete, cheap mechanism (diff two `List[Cluster]` snapshots) rather than a new LLM
judgment call.

---

## Phase 3 — Multi-persona selective coding (new — extends beyond the prior plan)

This is the newly-requested piece. Today, `select_dimensions` is one LLM call producing a relevance-filtered
subset with drop rationales — a useful step, but not classic selective coding (which integrates everything
around **one core category**, chosen by analyst judgment, not a mechanical filter).

**Design**: run `select_dimensions` once per persona over the same reconciled taxonomy from Phase 2, each
persona independently producing (a) its own relevance-ranked `selected_ids`/`dropped` judgment, exactly
like today's `SelectionOutput`, and (b) a **nomination of which single dimension it considers the core
category** for this `use_case` — a small, cheap addition to `SelectionOutput` (one more field: `core_nomination:
Optional[str]`).

**Reconciliation, combining two independent signals** (again following Nelson's confirmation principle —
two differently-sourced signals agreeing is real evidence, one signal alone is not):

1. **Relevance**: keep a dimension if a majority of personas selected it; route dimensions with a near-even
   split to one adjudicating LLM call (same borderline-band pattern already used for value merges and for
   Phase 2's dimension reconciliation) rather than deciding by raw vote count alone.
2. **Core category**: the dimension most personas nominate as core is one candidate signal; independently,
   compute simple graph centrality over the final `Relation` edges (most/strongest incoming+outgoing typed
   relations) as a second, structurally-derived candidate. When the two agree, that's a well-supported core
   dimension — a real, if lightweight, approximation of classic selective coding's central phenomenon,
   additive to (not a replacement for) the existing relevance filter. When they disagree, surface both
   candidates in the report rather than picking one arbitrarily — this is itself useful information about
   whether the corpus actually has a single obvious center or several competing ones.

This directly resolves `docs/GT_DESIGN_SPACE_ASSESSMENT.md`'s Part 4 finding that Delve's "selective coding"
doesn't do core-category integration and its enhancement E3 (optional core-dimension identification),
using multi-persona agreement as one of the two signals rather than graph centrality alone — which is more
faithful to how real selective coding is actually decided (analyst judgment, corroborated, not a pure
graph statistic).

---

## Phase 4 — The Explore capability: sampling unoccupied points

This is the direct implementation of "the space is an artifact that generalizes or opens up possibilities
of alternative solutions." It is built as a **separate, post-hoc capability** operating on a saved,
finished taxonomy JSON — architecturally sibling to `evaluation/consistency.py` (reads saved taxonomies,
orchestrates nothing) rather than a new mode inside the live LangGraph run. This keeps the mined,
evidence-grounded taxonomy and the exploratory artifact cleanly separated, per
`docs/GT_DESIGN_SPACE_ASSESSMENT.md`'s Guideline 1 — a sampled point is a hypothesis, not a finding, and the
report must never blur the two.

**Sampling.** For D selected dimensions with V₁...V_D values each, full enumeration is combinatorially
infeasible past a handful of dimensions (a 7-dimension, 3-value-average space is already ~2,187 points).
Default to random or diversity-maximizing sampling (greedy selection maximizing embedding distance between
candidate points' concatenated value labels) rather than exhaustive enumeration, with the sample size
configurable and always logged (per the Workflow-authoring guidance already followed elsewhere in this
project: no silent caps — state plainly how much of the space was actually sampled).

**Consistency filtering — the schema gap to be explicit about.** Shaw's own examples exclude points
because "the combinations of choices don't make sense" (e.g., a display-format decision is irrelevant if
nothing is displayed) — but Delve's `Relation` schema is *dimension*-level (precondition/consequence/
co_occurring/constrains between whole dimensions), not *value*-level, so it can't mechanically rule out
"this specific value of dimension A is incompatible with that specific value of dimension B." Two ways to
handle this, in order of effort:

- **Near-term (no schema change)**: for each sampled point, make one LLM judgment call — given the point's
  chosen values and the dimensions' `Relation`s as context, is this specific combination coherent for the
  `use_case`, and if not, why? This is pragmatic and immediately buildable, but per Nelson's confirmation
  principle it's a single method (LLM judgment) checking a single method's own output (the LLM-mined
  relations) — worth pairing with a second, cheaper signal: flag a point as *at minimum* worth a second
  look if it combines two values whose dimensions have a `constrains` or `precondition` relation between
  them, so the LLM judge always has that flag as context rather than reasoning from scratch each time.
- **Longer-term (schema change)**: extend `Relation` (or add a new value-level `Constraint` type) with
  optional value-to-value entries — a real fix, deferred here since it's a bigger schema change than this
  roadmap's scope, but named so `Cluster`/`Value`/`Relation` aren't accidentally designed to preclude it
  later (same forward-compatibility caution as the earlier hierarchy note).

**Diversity and novelty scoring.** Score each surviving candidate point against the *observed* points (the
actual value-combinations documents in the corpus were labeled with, from `label_documents`/test-mode
runs): a candidate close to an observed combination mostly validates the mined space (useful, but not
new); a candidate far from every observed combination is the genuinely novel "opportunity" reading of an
unoccupied point Shaw describes. Report both, distinctly labeled.

**Output.** A new, clearly-titled artifact — a "Design Space Exploration Report," structurally similar to
but explicitly distinct from the Grounded Theory Report — listing sampled points, their consistency
verdicts (kept / flagged / rejected, each with rationale), and their novelty scores, so a reader can never
mistake a generated candidate for a data-grounded finding.

---

## Sequencing and gating

Phase 0 gates whether Phases 1–3 are worth building at all, on your actual data, before any `graph.py`
surgery. Phases 1 → 2 → 3 build on each other (each reuses the persona list and the reconciliation pattern
established in the previous one) and should land in that order. Phase 4 has no dependency on Phases 1–3 —
it can be built and validated against the *current*, single-persona pipeline's output first, then pointed
at a Phase 2/3-reconciled taxonomy once that exists, since its input is just "a saved taxonomy JSON" either
way.

## Explicitly out of scope here, still valid, tracked elsewhere

`docs/GT_DESIGN_SPACE_ASSESSMENT.md`'s E1 (gap-directed minibatch ordering), E2 (surface the memo trail),
E5 (close the negative-case/fallback-bucket feedback loop), and E6 (distill a lightweight test-mode
classifier per TnT-LLM's actual Phase 2) are unaffected by this roadmap and remain queued independently —
none of them conflict with or depend on the multi-persona/exploration work above.
