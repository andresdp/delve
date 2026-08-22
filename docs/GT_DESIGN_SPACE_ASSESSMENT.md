---
title: Grounded Theory ↔ Design Space — a methodology assessment
description: How Delve's LangGraph pipeline maps onto grounded-theory methodology and Mary Shaw's design-space framework, where the blend is coherent, and where it needs work — scoped to 1-level (flat) taxonomies.
generated: 2026-08-21
---

# Grounded Theory ↔ Design Space: A Methodology Assessment

## Purpose and sources

This document assesses how faithfully Delve's pipeline implements grounded theory (GT) methodology,
how GT's outputs should blend with Mary Shaw's notion of a *design space*, and what that implies for
Delve's current 1-level (flat) taxonomy mining. It draws on:

- **Classic and contemporary GT literature**: Straussian coding stages ([MAXQDA's axial coding
  guide](https://www.maxqda.com/research-guides/axial-coding), [Delve Tool's open/axial/selective coding
  guide](https://delvetool.com/blog/openaxialselective) and [grounded theory
  guide](https://delvetool.com/blog/groundedtheory) — an unrelated qualitative-research tool that happens
  to share this project's name), a comprehensive academic overview of Glaserian, Straussian, and
  constructivist (Charmaz) variants ([Grounded Theory Approaches: A Comprehensive
  Review](https://files.eric.ed.gov/fulltext/EJ1385933.pdf)), and [Axial
  coding](https://en.wikipedia.org/wiki/Axial_coding) on Wikipedia.
- **Recent computational/LLM-assisted GT work**: a human-in-the-loop computational GT framework for
  large qualitative datasets ([Alqazlan et al.,
  2025](https://journals.sagepub.com/doi/10.1177/20539517251347598)), and the broader landscape of LLMs
  applied to qualitative coding ([Large Language Model for Qualitative Research: A Systematic Mapping
  Study](https://arxiv.org/html/2411.14473v3), [ChatGPT to conduct Grounded Theory: a JMIR
  tutorial](https://www.jmir.org/2025/1/e70122), [Computational Grounded
  Theory](https://www.emergentmind.com/topics/computational-grounded-theory)).
- **Mary Shaw, "The Role of Design Spaces,"** *IEEE Software*, Jan/Feb 2012 — read in full from
  `paper/ShawDesignSpace-a.pdf` in this repo.
- **TnT-LLM: Text Mining at Scale with Large Language Models** (Wan et al., Microsoft, 2024) — read in
  full from `paper/TNT-LLM-2403.12173v1.pdf`; Delve's own docs describe its pipeline as
  "TnT-LLM-style," and this is the more direct methodological ancestor than the GT literature itself
  (see Part 2).
- **Delve's own implementation**: `src/taxonomy_generator/graph.py`, the `nodes/`, `prompts/`, and
  `schemas.py`, plus `CONCEPTS.md`, `docs/TAXONOMY_QUALITY_PLAN.md`, and `docs/NEW_IDEAS.md`.

## Part 1 — What "grounded theory" means, precisely

Grounded theory is a family of methods (Glaser & Strauss originally; Strauss & Corbin's more structured
variant; Charmaz's constructivist variant) for building a theory *from* qualitative data rather than
testing a theory brought *to* the data. Despite real differences between the variants, they share eight
characteristics relevant here: process orientation, theoretical sensitivity, theoretical sampling,
constant comparative analysis, core-category identification, memo-writing, cautious literature
integration, and theory production as the end goal — not just a coded, organized description of the
data.

The Straussian coding sequence, which Delve's own vocabulary follows most closely:

- **Open coding** — data broken into fragments and given provisional conceptual labels (word-by-word,
  line-by-line, or incident-by-incident), asking who/what/where/when/why of each fragment.
- **Axial coding** — fragments regrouped into higher-level categories; a *conditional matrix* relates
  each category's causal conditions, the context, intervening conditions, the actions/interactions taken,
  and the consequences that follow.
- **Selective coding** — once roughly a handful of categories have emerged, the analyst identifies **one
  core category** — the central phenomenon — and systematically relates every other category to it,
  producing an integrated theoretical narrative (a storyline), not just a filtered list.
- **Constant comparison** runs throughout: every new incident is compared against existing categories,
  refining category boundaries continuously rather than only at defined checkpoints.
- **Theoretical sampling** means the *next* data to examine is chosen deliberately, based on where the
  emerging theory is thin or ambiguous — sampling follows the concepts, not a pre-fixed batch order.
- **Memoing** is a first-class, accumulating artifact: analytic notes about categories, hypotheses, and
  open questions, written throughout — the record of the theory's own evolution, not just its final
  state.
- **Theoretical saturation** is reached when new data stops adding new properties, dimensions, or
  relationships to the theory — a broader judgment than "no new instances of what we already have."

One vocabulary collision matters for reading GT sources literally against Delve's schema: in classic GT,
a category's **"dimension"** usually means *a property's range of variation within that category* (e.g.
category "Pain," property "intensity," dimension "mild ↔ severe") — a different, *nested* sense of the
word than Shaw's or Delve's top-level "Dimension" (an orthogonal axis of the whole design space). Delve's
`Cluster` (top-level Dimension) is closer to a classic GT *category*; a classic GT "dimension" is closer
to the *range spanned by* one of Delve's `Value`s. Worth a short clarifying note in `CONCEPTS.md` so
readers coming from the GT literature don't misapply the term.

## Part 2 — What a design space is, precisely (Shaw, 2012)

Shaw's design space is a **discrete Cartesian space**: design *decisions* are the dimensions, the
*alternative choices* for each decision are values on that dimension, and a **complete design is a
point** in the space. Three details matter beyond that headline definition:

1. **Dimensions aren't independent.** Choosing one alternative can preclude or make irrelevant the
   alternatives on another dimension (Shaw's example: if displaying a value is optional, the display
   format dimension is irrelevant when nothing is displayed). A design space representation has to
   capture these interactions, not just list orthogonal axes and pretend they're isolated.
2. **A design space representation is deliberately a slice.** "Most interesting design spaces are too
   rich to represent in their entirety, so design space representations feature dimensions corresponding
   to the properties of principal interest." A good representation is scoped to the properties that
   matter for a *particular* task or comparison, not maximal coverage of every conceivable axis.
3. **The representation is naturally hierarchical**, not flat. Shaw's dimension-oriented tree form has
   two kinds of branches: **choice branches** ("##", the actual decisions — usually pick one) and
   **substructure branches** (unflagged groupings of independent sub-decisions — usually explore all of
   them). Her worked example (a traffic-signal simulator) has 7 top-level dimensions, several of which
   nest several levels deep (e.g. Road System → Intersections → "Place in hierarchy" → choices). And
   **unoccupied points in the space are meaningful, not noise** — Shaw explicitly notes they can indicate
   either an infeasible combination or "an opportunity for new products."

Also worth noting for method, not just definition: Shaw's own traffic-signal design space was built by
**manually open-and-axial-coding qualitative data** — she "studied the videos and transcripts and
identified the principal conceptual entities the teams included in their designs along with any
alternatives they considered," organizing them into dimensions "trying to remain faithful to the
structure that emerged from the design discussions." She then **triangulated** that bottom-up analysis
against two other sources — the task's written prompt, and a mature commercial product (Trafficware) —
and visually tagged which dimension values came from which source (red boxed text for the prompt,
plain text for team decisions, yellow highlight for the commercial tool) in one unified tree. This is,
in effect, Shaw doing GT-style coding by hand across **three distinct data sources with different
epistemic status**, then presenting the result as a design space. That precedent is a strong argument
for treating source/provenance as a first-class thing to preserve (see Part 5), and it's a direct
real-world analogue of the multi-persona idea already logged in `docs/NEW_IDEAS.md`.

## Part 3 — Where GT and design spaces agree, and where they genuinely don't

They agree on structure more than either literature usually says explicitly: a GT category with its
properties, differentiated from other categories, is not far from a design dimension with its values,
differentiated by orthogonality. GT's insistence that categories must be *grounded in data* — every
category traceable to specific incidents — maps directly onto Shaw's dimensions and values being
*populated with actual instances* (her Table 1, her `[email]`/`[wiki]` tags). And GT's paradigm model
(conditions → actions/interactions → consequences) is a real ancestor of Shaw's "dimensions aren't
independent" — both are ways of saying a flat list of categories/dimensions is an incomplete
representation without their interactions.

They genuinely diverge on two points that matter for Delve:

- **GT's output is descriptive of what the data contains; a design space is also prescriptive/comparative
  of what could be built.** GT stops at "here is the theory the data supports." Shaw's design space is
  explicitly also useful for **unoccupied points** — combinations nobody has built, flagged as
  opportunities. A design space mined purely by GT rules (every value must have supporting evidence) is
  a *populated subset* of the full conceptual space Shaw describes, not the space itself. That's not a
  flaw — a data-grounded design space is a genuinely useful, honestly-scoped artifact — but the two
  should not be conflated in how results are presented (see Part 5, "keep provenance status visible").
- **GT's selective coding integrates around one core category; a design space (at least in Shaw's
  1-level slice) doesn't require a center.** Classic selective coding produces a storyline: everything
  relates to the central phenomenon. Shaw's flat dimension list has no such requirement — dimensions are
  peers, distinguished only by which ones matter for the task at hand.

## Part 4 — Stage-by-stage assessment of Delve's current implementation

| GT / design-space concept | Delve's implementation | Fidelity |
|---|---|---|
| Open coding | `open_code_minibatch` → `OPEN_CODING_PROMPT`, per document, 0–8 codes with a label + rationale, grounded in the `use_case` | **Faithful.** Matches the classic definition closely — fine-grained, per-incident, use-case-scoped. |
| Axial coding | `generate_taxonomy` / `update_taxonomy` organize open codes into `Cluster`s (dimensions) with `Value`s and typed `Relation`s | **Faithful in spirit, reinterpreted in shape.** The four `Relation` types (`precondition`, `consequence`, `co_occurring`, `constrains`) are a compact, workable stand-in for the Straussian conditional matrix — but applied *pairwise between whole dimensions*, not oriented around one case's conditions/actions/consequences. That's a reasonable adaptation for a design-space framing, not a defect, but it's worth naming explicitly rather than implying a 1:1 match to the paradigm model. |
| Selective coding | `select_dimensions` filters the reviewed taxonomy to what's relevant to the `use_case`, keeping drops-with-rationale | **Real divergence.** This is a relevance *filter*, not classic selective coding's core-category integration. Both `CONCEPTS.md` and the prompts call it "selective coding," which invites a false equivalence. It's a genuinely useful step — just a different one. See Part 5 for a concrete way to add real core-category identification alongside it, not instead of it. |
| Constant comparison | `update_taxonomy` compares each new minibatch against the existing taxonomy; `value_consolidator.py` does embedding + LLM-adjudicated merging of near-duplicate values within a dimension | **Faithful**, at the value level especially — this is close to constant comparison's textbook description. Granularity is per-minibatch (`batch_size` documents) rather than per-incident; that's a reasonable, tunable concession to LLM call cost, not a conceptual gap. |
| Theoretical sampling | `generate_minibatches` shuffles document indices with `random_seed` and slices into fixed-size batches; batch order does not change once computed | **Not implemented — this is the biggest gap.** Classic theoretical sampling means choosing what to examine *next* based on where the theory is thin. Delve's saturation checker already surfaces exactly the right signal (`uncovered_concepts` per minibatch, in `saturation_history`) but nothing currently uses it to reorder the *remaining* minibatches. See Part 6, enhancement E1. |
| Theoretical saturation | `check_saturation` compares one minibatch's open codes against the current taxonomy; a streak of saturated minibatches (`saturation_streak_threshold`) ends the update loop | **Faithful but narrower than the textbook definition.** GT saturation is "no new properties, dimensions, *or relationships*" — Delve's check is concept-coverage only (does an open code fit an existing dimension), not relationship-coverage (are new `Relation`s still emerging between dimensions). A corpus could look saturated on concepts while still revealing new cross-dimension dependencies. See Part 6, enhancement E4. |
| Memoing | `TaxonomyOutput.explanation` (one prompt-mandated paragraph per generate/update/review call) accumulates in `state.explanations` via `Annotated[List[str], operator.add]` | **Exists as data, invisible as artifact.** The accumulator is already there — nothing is thrown away — but per `CONCEPTS.md`'s own definition, the Grounded Theory Report's Narrative Summary is built only from the *latest* iteration's rationale and dimension descriptions. The full memo trail — the record of how the theory changed and why, iteration by iteration — isn't rendered anywhere. This is GT's most distinctive practice and Delve's cheapest fix. See Part 6, enhancement E2. |
| Negative case analysis | Prompts explicitly instruct against "Other"/catch-all dimensions; test-mode `delta_summary` reports the fallback-bucket document count | **Reported, not acted on.** Persistent negative cases (documents that keep landing in the fallback bucket) are GT's classic signal to refine or extend the theory. Delve surfaces the count but doesn't feed it back into anything. This is the same seam as the existing `docs/NEW_IDEAS.md` question about a review-node feedback loop. See Part 6, enhancement E5. |
| Core category / theoretical integration | Not implemented; dimensions are peers with no designated center | **Absent by design**, and arguably correctly absent for a *1-level* design space per Shaw's own flat slices (Figure 1/2) — but worth a lightweight, optional version. See Part 6, enhancement E3. |
| Multiple coders / inter-rater reliability | Single fixed system prompt and model at every LLM-calling node | **Absent.** Already scoped in detail as options A and B in the most recent `docs/NEW_IDEAS.md` entry ("Multi-persona grounded theory") — this is Delve's answer to GT's coder-triangulation tradition and to the "multiple annotators assess quality" checkpoint the computational-GT literature treats as a rigor requirement, not a nicety. Not repeated here; see that entry. |
| Coverage / accuracy / relevance evaluation | `evaluation/judge.py`, `metrics.py`, the Scoreboard (per `CONCEPTS.md`) | **Faithful and broader than its own ancestor.** TnT-LLM's paper proposes exactly three criteria — coverage (fallback-bucket proportion), label accuracy, and use-case relevance — as its evaluation suite; Delve's Scoreboard already implements a richer superset (orthogonality, clarity, completeness, no-catch-alls, axis-vs-value, per `docs/TAXONOMY_QUALITY_PLAN.md`'s Appendix A) and correctly treats it as **observe-only** (`CONCEPTS.md`: never routes the graph or modifies the taxonomy) — which lines up with the computational-GT literature's explicit warning against blind trust in automated topic-quality metrics. |
| Taxonomy generation "at scale" | `label_documents` calls an LLM per document against the final taxonomy | **Divergence from TnT-LLM's own Phase 2.** TnT-LLM's actual proposal for scale is to use LLM labels as *pseudo-labels* to train a cheap downstream classifier (logistic regression / MLP over embeddings) so future classification doesn't need an LLM call per document. Delve implements TnT-LLM's Phase 1 (taxonomy generation) closely but not this distillation step of Phase 2 — every classified document still costs one LLM call. See Part 6, enhancement E6. |

## Part 5 — Guidelines for keeping the GT ↔ design-space blend coherent

1. **Say "empirically-grounded design space," not just "design space," when describing Delve's output.**
   Every `Value` Delve produces has `supporting_doc_ids` — it is, correctly, a *populated subset* of the
   full conceptual space Shaw describes, not the space itself. This is a genuine strength (it's honest,
   and it's what makes the grounded theory report trustworthy) — but reports and downstream consumers
   should never present it as if it were an exhaustive or normative design space. When "sample points
   that combine values across dimensions" (already in `docs/NEW_IDEAS.md`) is eventually built, its
   output is a *different, hypothesis-generating* artifact — occupying Shaw's "opportunity" reading of
   unoccupied points — and should be labeled distinctly from the mined, evidence-backed taxonomy, not
   merged into the same report section.

2. **Keep dimensions flat for now, but design the schema so a future hierarchical extension doesn't
   require a rewrite.** Shaw's own representation is a tree with choice vs. substructure branches; TnT-LLM's
   own paper notes its pipeline "naturally lends to hierarchy" by recursively re-running Stage 2 per
   category. The clean way to get there later without disturbing the current 1-level scope: treat a
   selected `Cluster`'s supporting documents (via its values' `supporting_doc_ids`) as the corpus for a
   *recursive* sub-run of the same `open_code_minibatch → generate/update_taxonomy → check_saturation`
   subgraph, producing sub-dimensions nested under that one dimension — Shaw's substructure branch,
   TnT-LLM's suggested extension, and Delve's existing subgraph, all lining up. Not proposed as near-term
   work, just noted so the current schema (`Cluster`, `Value`) isn't accidentally designed to preclude it
   (e.g., avoid hard-coding a global flat numbering scheme for `id`s that couldn't accommodate a
   `parent_id`later).

3. **Preserve source/provenance the way Shaw's own worked example did.** Her tree tags every value with
   which source it came from (a team's design decision, the task prompt's implication, or a commercial
   product's choice) using different visual markup for each — never blending them anonymously. Delve
   already has an analogous mechanism (`supporting_doc_ids`), but as more source diversity gets added
   (the Cursor-git-at-scale corpus's mixed decision/tradeoff/lesson documents; a future multi-persona
   pipeline's per-persona drafts) it becomes worth surfacing *what kind* of source supported a value, not
   just which documents did — directly useful for the multi-persona reconciliation work already scoped in
   `docs/NEW_IDEAS.md`.

4. **Don't let "selective coding" quietly mean two different things.** Keep `select_dimensions` exactly
   as it is (a use-case relevance filter is genuinely useful and matches Shaw's "representation is
   deliberately a slice" idea) — but if a more classically GT-faithful integration step is wanted later,
   build it as an *additional*, clearly-named step (e.g. "core dimension identification"), not by
   redefining what `select_dimensions` already does well.

5. **When citing GT terminology in docs or prompts, flag the "dimension" collision once, explicitly.**
   A one-line note in `CONCEPTS.md` — "Delve's Dimension is a design-space axis (Shaw); it is not the
   same as a GT 'dimension,' which names a property's range within a category" — prevents a reader who
   knows the GT literature from misreading the schema.

## Part 6 — Prioritized enhancements

Ordered roughly by effort-to-value; each ties back to a specific gap identified in Part 4.

- **E1 — Gap-directed minibatch ordering (approximates theoretical sampling).** `check_saturation`
  already records `uncovered_concepts` per minibatch in `saturation_history`. Low-effort version: after
  each saturation check, re-rank the *remaining* (not-yet-processed) minibatches by embedding similarity
  between their documents' summaries and the reported uncovered concepts, and process the most relevant
  one next instead of the next one in the fixed shuffle. This is the closest a fixed, pre-collected
  corpus can get to real theoretical sampling — it can't fetch new data, but it can choose intelligently
  among the data already collected.

- **E2 — Surface the memo trail in the Grounded Theory Report.** `state.explanations` already
  accumulates every iteration's rationale via `operator.add`; nothing renders it. Add an "Evolution of
  the Taxonomy" section to `report_renderer.py` that lists each iteration's stored explanation in order —
  this is GT's most distinctive practice (memoing) and the data for it already exists in state, unused.
  This also directly extends the "evolution of thinking" framing already explored for the Cursor
  git-at-scale corpus, but for Delve's *own* theorizing process rather than a case study's.

- **E3 — Optional core-dimension identification for narrative framing.** Compute simple graph centrality
  over the final `Relation` edges (which dimension has the most/strongest incoming and outgoing typed
  relations) and let the Narrative Summary optionally lead with that dimension as the organizing thread —
  a lightweight, non-invasive approximation of classic selective coding's core category, additive to
  `select_dimensions` rather than a replacement for it (Guideline 4).

- **E4 — Broaden saturation to cover relationships, not just concepts.** Extend
  `SaturationCheckOutput`/`SATURATION_CHECK_PROMPT` to also ask whether the minibatch's open codes imply
  any *new* cross-dimension relation not already captured, not only whether the concepts themselves fit
  existing dimensions. A corpus can look concept-saturated while still teaching the taxonomy new
  dependencies.

- **E5 — Close the negative-case feedback loop.** When `delta_summary`'s fallback-bucket count exceeds a
  configurable threshold in test mode, surface an explicit recommendation (or an automated re-entry point)
  back into train mode refinement, rather than only reporting the count. This is the same seam as the
  existing `docs/NEW_IDEAS.md` question about a feedback loop (return arc) in the review node — this
  gives it a concrete trigger condition.

- **E6 — Distill a lightweight classifier for test-mode labeling, per TnT-LLM's actual Phase 2.**
  Once a taxonomy is frozen (test mode), use `label_documents`' LLM-produced labels on a representative
  sample as pseudo-labels to train a small classifier (e.g. logistic regression over the existing
  `embedding` model's vectors) for classifying the rest of the corpus, reserving the LLM call for
  documents the classifier is unsure about. This is what TnT-LLM's own paper found gives "at scale"
  classification its actual scalability — Delve currently implements TnT-LLM's Phase 1 faithfully but
  stops short of this part of Phase 2.

- **Already scoped elsewhere in `docs/NEW_IDEAS.md`, not repeated here**: the multi-persona open-coding
  and axial-coding options (Delve's answer to GT's multiple-coder/inter-rater tradition), the
  sample-points-in-the-space idea (Shaw's "opportunity" reading of unoccupied points — see Guideline 1
  on keeping it labeled distinctly from the mined taxonomy), and the standalone LLM-judge scoreboard
  (already a faithful superset of TnT-LLM's own coverage/accuracy/relevance evaluation triad, per Part 4).
