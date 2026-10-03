---
title: SANER 2027 (Agentic AI4SE track) — paper plan for Delve
description: Working plan for a research paper evaluating Delve as a multi-agent Straussian grounded-theory pipeline for mining design spaces / architectural design decisions. Covers the implementation backlog in the current codebase, the experiment protocol, the paper's storyline and outline, timeline, and open decisions.
created: 2026-09-26
updated: 2026-09-26
status: draft — living document
---

# SANER 2027 Paper Plan — Delve

**How to read this document**

- §1–§2: constraints and current state.
- §3: the story the paper tells.
- §4–§5: benchmark and metrics.
- §6–§7: the agentic and Straussian design rationale.
- **§8: what to implement or adjust in the codebase.**
- **§9: the experiment protocol.**
- **§10: the paper outline, storytelling, figures and reviewer defence.**
- §11–§14: timeline, decisions, risks, references.

---

## 1. Venue and hard constraints

- **Track**: SANER 2027 — Agentic AI4SE
  (<https://conf.researchr.org/track/saner-2027/saner-2027-agentic-ai4se-track>).
- **Scope keywords that fit Delve**: agent systems for software analysis and comprehension; multi-agent
  workflows with coordination and delegation; planning/memory/tool use/feedback mechanisms; benchmarking
  and evaluation of agent systems; human–agent collaboration; datasets and tools for research.
- **Format**: 10 pages + 2 pages of references, IEEE `\documentclass[10pt,conference]{IEEEtran}`,
  **double-anonymous** (no identifying links; self-citations in third person; anonymized replication
  package, e.g. anonymous.4open.science).
- **Review criteria**: relevance to agentic AI4SE, originality, significance, soundness, **evaluation
  quality (tasks, baselines, metrics, datasets, studies)**, **open science / verifiability**, presentation.
- **Deadlines (AoE)**: abstract **2026-10-19**, paper **2026-10-23**, notification 2026-12-08,
  camera-ready 2027-01-08.

Consequence: roughly four weeks. **Pipeline code freeze on 2026-10-06** (tag `saner27-freeze`). After the
freeze, only bug fixes are allowed, and every fix is logged in the replication package.

---

## 2. Current status of Delve (as of 2026-09-26)

### 2.1 Strengths to build on

- **End-to-end LangGraph pipeline** (`src/taxonomy_generator/graph.py`): `load_corpus` → (optional)
  `summarize` → `get_minibatches` → `open_code_minibatch` → `generate_taxonomy` / `update_taxonomy` →
  `evaluate_taxonomy` (scoreboard fed back into the next iteration) → `check_saturation` (streak-based
  termination; uncovered concepts fed back as critic feedback) → `review_taxonomy` → `consolidate_values`
  (embedding + LLM adjudication) → `select_dimensions` → `evaluate_taxonomy_final` → `label_documents`
  (→ `aggregate_new_values` in test mode).
- **Design-space schema** (`schemas.py`): `Cluster` (dimension) → `Value` (option, with `status`
  accepted/rejected/outcome and `supporting_doc_ids`) + dimension-level `Relation`
  (precondition / consequence / co_occurring / constrains).
- **Evaluation infrastructure**:
  - GEval scoreboard with 10 criteria (`evaluation/metrics.py`, `evaluation/runner.py`);
  - N-way consistency comparison (`evaluation/consistency.py::compare_taxonomies`);
  - run metrics (tokens) persisted into the saved taxonomy JSON.
- **Human-in-the-loop between runs already works**: `--taxonomy <saved.json>` seeds a train-mode run;
  `--feedback` / `--feedback-file` (or `feedback:` in config) become persistent `external_feedback` in the
  generation/update/review prompts.
- **Existing ablation switches**:
  - `taxonomy.consolidate_values` (value consolidation off);
  - `evaluation.enabled` (scoreboard, and therefore judge feedback, off);
  - `taxonomy.saturation_streak_threshold` (set above the number of minibatches to disable early stopping);
  - `summarization.skip`;
  - `pipeline.random_seed`.
- **Unit tests exist**: 9 files in `tests/unit_tests/` (schemas, prompt content, metrics, feedback
  formatting, HTML report, run metrics, …). The OpenWiki "no tests" note is stale.
- **Reports**: Grounded Theory Report (Markdown), unified HTML report, PCA biplots.
- **Methodological write-ups** usable for Approach/Related Work: `docs/GT_DESIGN_SPACE_ASSESSMENT.md`,
  `docs/DESIGN_SPACE_ROADMAP.md`, `docs/VALIDATION_STUDIES.md`, `docs/NEW_IDEAS.md`.

### 2.2 Gaps a reviewer would find

1. **No ground-truth evaluation, baselines, or ablations**. The scoreboard is intrinsic (LLM judging LLM).
2. **Tiny example corpora** (12–28 short snippets: campus-bike, das-p1-2023, pharmacy-food,
   cursor-git-at-scale). Fine as illustrations, not as evidence.
3. **Agentic framing**: fixed-topology workflow; no decision about what to read next.
4. **Grounded-theory fidelity**: see §7. Drivers and consequences are not first-class, relations exist only
   between dimensions, there is no theoretical sampling, saturation covers concepts only, the "selective
   coding" step is a relevance filter, and memos are not surfaced.

### 2.3 Code-level issues discovered while planning (must fix for the study)

| Issue | Where | Why it matters for the paper |
|---|---|---|
| **Open coding reads the 20-word summary when summarization is on** | `nodes/open_coder.py::_doc_input` (prefers `summary`); `config.yaml: summarization.summary_length: 20` | Gray-literature sources are thousands of words; coding summaries destroys evidence and grounding. Must code raw passages |
| **No segmentation of long sources** | `nodes/corpus_loader.py`, `utils.py::docs_from_dicts` | GT codes incidents, not whole articles; also context-length and cost control |
| **Judge is OpenAI-only** | `evaluation/metrics.py` (deepeval `OpenAIModel`), `evaluation/consistency.py::_adjudicate_same_dimension` (`AsyncOpenAI`) | A cross-family judge (validity safeguard) needs a provider-agnostic judge wrapper |
| **Drivers are prompt-only** | `prompts/taxonomy_generation.md` / `taxonomy_update.md` ("quality-attribute anchoring"), no schema field | Cannot measure driver recall against ground truth |
| **No ablation switch for open coding, review, decision status, judge feedback** | `graph.py`, routing, prompts | Needed for RQ3 |
| **No experiment harness** | — | ~200 runs need reproducible configs, output registry, cost logging |

---

## 3. The story

### 3.1 One-sentence thesis

> A multi-agent workflow that follows the Straussian grounded-theory procedure can reproduce most of the
> architectural design decision models that experts took months to build from the same gray literature.
> It stays traceable to verbatim evidence and costs a fraction of the effort. Its GT-specific agentic
> components, not just the LLM, are what make the difference over topic mining and single-prompt
> summarization.

### 3.2 Narrative arc (what the reader should believe after each section)

1. **Motivation**: design spaces and ADD models help practitioners avoid the "first alternative that comes
   to mind" (Shaw). Building them rigorously (Straussian GT over 20–30 gray-literature sources) costs months
   per domain, while the domains keep appearing (ML, RL, digital twins, agents…).
2. **The naive approaches fail in characteristic ways**: topic mining yields *themes* ("reward hacking",
   "monitoring") rather than *decisions with alternatives*; a single long-context prompt yields plausible
   but untraceable, unstable models. A motivating example (Fig. 1) contrasts a BERTopic topic, a
   single-prompt output, and an expert ADD for the same sources.
3. **Idea**: treat the GT procedure itself as the agent architecture. Each Straussian phase is carried by
   agent roles with explicit artifacts (codes, memos, a paradigm-model taxonomy) and feedback loops: Coder
   (open coding), Taxonomist ⇄ Critic (axial coding until saturation), Integrator (selective coding), plus
   optional human feedback.
4. **Evidence**: on two published expert studies (ML workflow and RL monitoring), Delve recovers X% of
   expert decisions and Y% of options with Z% grounding precision. It beats topic mining, matches or beats
   the long-context LLM on recall while being more traceable and stable, and ablations show which
   agentic/GT components matter.
5. **Beyond ground truth**: on a single-source engineering narrative (Cursor's "Git at any scale"), Delve
   produces a design space in which each organization's system (GitHub, Google, Microsoft, Cursor)
   appears as a distinct point, as in Shaw's original multi-team analysis. Experts judge it valid and
   useful.
6. **Takeaway**: LLM agents can act as *instruments* in a human-led GT study (a first pass plus traceable
   evidence plus expert feedback), not as autonomous theorists. We release ADD-Bench and the pipeline.

### 3.3 Running example

Use the **RL-monitoring study** (most recent, lowest contamination risk). Pick one ADD (e.g. *Reward
Hacking Detection Strategy*, 9 options, 16 drivers) and trace it end to end through the paper:
source passage → open code (with evidence quote and code kind) → value in the taxonomy → driver impact →
match against the expert option. This becomes the figure a reader remembers (Fig. 3).

### 3.4 Contributions (as they will appear in the introduction)

1. **Delve**: a multi-agent workflow that operationalizes Straussian GT for design-space mining. Four agents
   map to the GT phases: a Coder (open coding), a tool-using Taxonomist and a Critic in the axial-coding
   loop, and an Integrator (selective coding); a human expert can give feedback between runs.
2. **ADD-Bench**: an evaluation kit seeded with two published Straussian-GT ADD studies (sources,
   passages, expert ADD models as JSON), with a matching protocol and metrics, designed to be extended with
   further studies.
3. **Empirical evaluation**: fidelity against expert models, baselines, ablations of agentic/GT components,
   stability and cost, and a human-in-the-loop round, plus a case study without ground truth.
4. **Open-source artifacts**: pipeline, benchmark, all run outputs, and analysis scripts.

### 3.5 Research questions

| RQ | Question | Main evidence |
|---|---|---|
| RQ1 Fidelity | How closely do Delve-mined design spaces reproduce expert GT-derived ADD models from the same sources? | P/R/F1 at ADD, option, driver, relation level; grounding precision; expert validity of unmatched items |
| RQ2 Baselines | How does Delve compare with topic modeling and LLM baselines? | Same metrics for BERTopic, TnT-LLM-style, long-context LLM (+ LLooM) |
| RQ3 Components | Which agentic and Straussian components contribute to quality? | Ablations |
| RQ4 Stability and cost | How stable and how costly is Delve? | Cross-seed agreement, tokens, $, wall-clock |
| RQ5 Human-in-the-loop (optional) | Does one round of expert feedback improve the model? | ΔF1 run 1 → run 2 |
| RQ6 Beyond ground truth | Does Delve produce a valid, useful design space for a single-source engineering narrative with no expert model? | Expert assessment; system × dimension placement (Shaw's Table 1 analogue); stability; sensitivity to corpus preparation |

---

## 4. Ground truth: ADD-Bench

### 4.1 Case studies covered in the paper (decided)

| # | Case | Ground truth | Role in the paper |
|---|---|---|---|
| C1 | **ADDs for the ML Workflow** (Warnett & Zdun; IEEE Software 2021/22) | Yes: expert ADD model in Zenodo 10.5281/zenodo.5730291 (CodeableModels + coding data) | GT study; older, so likely seen in pre-training (contamination contrast with C2) |
| C2 | **ADDs for Monitoring Deployed RL Systems** (Fang, Warnett, Zdun; 2026) | Yes: expert ADD model in Zenodo 10.5281/zenodo.20305497 (CodeableModels) | GT study; **running example**, held out from all tuning; likely post-dates training cut-offs |
| C3 | **Cursor "Git at any scale"** (`examples/cursor-git-at-scale/`) | No | Case study without ground truth (RQ6); different genre (single-source engineering narrative with several organizations' solutions) |
| C4 *(stretch)* | **Lane's user-interface architecture design space** (T.G. Lane, CMU/SEI-90-TR-22, 1990; thesis CMU-CS-90-101) | Yes (the expert space in TR-22 Appendices A and B) | Stretch goal only; see §4.5. A classic, flat, driver-rich space; in the paper only if the go/no-go check passes |

**Not covered in the paper**:
- *Design Decisions for Architecting Digital Twins* (SEAA 2025; Zenodo 15514330) — optionally a **private
  development set** for calibration (§9 E0). Never reported as a result.
- *Engineering Decisions in MARL Systems* — repository mining, not a GT model. Out of scope.

C1 and C2 fit because they follow **the procedure Delve automates** on a **closed, published source list**
(29 sources each) and publish **machine-readable models**. They also form a natural pair for contamination:
C1 (2021) is probably in the models' training data; C2 (2026) probably is not.

**Two ground-truth views per study (decided 2026-10-01).** Every metric is computed against both, and
both are reported side by side:
- **Paper view** (`gt_paper.json`): the decisions, options, drivers and relations as **reported in the
  published paper** (text, tables and figures). It is what a reader can check against the article.
- **Model view** (`gt_model.json`): the **full model in the replication package** (CodeableModels). It is
  the complete expert model.

The two differ, and the differences are documented in the benchmark datasheet (B5) and reported in the
paper. A crosswalk records, for every element, whether it appears in the paper, the model, or both. The use
case is the same for both views: it is written from the study's overall scope, never from either view's
content.

**C1 specifics**: the article describes only a *subset* of the modelled ADDs (data ingestion/processing,
model building, AutoML). It explicitly omits deployment, CI/CD, MLOps and development environments,
although sources s20–s29 (MLOps, monitoring, Jupyter) feed exactly those parts. So the paper view is much
smaller than the model view. Source links are 2021 TinyURLs pointing to archived copies (all 29
recovered).

**C2 specifics**: the paper's Table 2 lists 57 options (ADD 2: 16, ADD 6: 9) and quotes 59/72 drivers; the
model has 62 options (ADD 2: 15, ADD 6: 15) and 43 forces. Both views are kept as they are; the differences
are reported. The package also classifies sources as primary/supporting/confirming (useful for E5).

**Threat to state**: both GT studies come from the same research group (single-group bias). The kit is
designed to be extended; name candidate studies as future work.

### 4.2 Terminology mapping: Delve ↔ the papers (C1/C2) ↔ Straussian GT ↔ Shaw

The paper will use one vocabulary consistently. **Proposed convention for the paper's text**:
- *decision point* (= Delve dimension = the papers' ADD/"decision"): a topic phrased as one question that
  requires a choice;
- *candidate decision* (= Delve value = the papers' "option"): an alternative answer to that question;
- *driver*, *impact*, *relation*.

A well-formed decision point passes one test: all its candidate decisions are alternative answers to one
question. A broad topic whose values answer different questions bundles several decision points and is
misleading (agreed 2026-10-01; enforced in the generation, update, review and selection prompts). Delve
identifiers (`Cluster`, `Value`, …) appear only in the Approach section and the replication package.

#### 4.2.1 Core model elements (these are what get matched)

| Delve term (code) | Papers' term (C1 Warnett & Zdun; C2 Fang et al.) | Straussian GT | Shaw design space | Comparison rule |
|---|---|---|---|---|
| **Taxonomy** / design space (`clusters[-1]` after review + consolidation; `selected_clusters` after selection) | **ADD model** (decision model, rendered as UML via CodeableModels) | The (substantive) theory | Design space representation (a "slice") | Primary comparison view: the **full consolidated taxonomy**. `selected_clusters` is secondary |
| **Dimension** (`Cluster`: `id`, `name`, `description`) | **Architectural design decision (ADD)**, "Decision" in the UML (e.g. C2 *ADD6 Reward Hacking Detection Strategy*) | Category / phenomenon | Dimension (a design decision) | Unit of **decision-level** matching |
| **Value** (`Value`: `label`, `description`) with status `accepted` or `rejected` | **Decision option** ("solution"; CamelCase names in the papers, e.g. *ConservativePolicyUpdates*) | Action/interaction strategy | Alternative (a value on a dimension) | Unit of **option-level** matching. Accepted **and** rejected values both count as options (the GT lists every considered option; it has no status) |
| **Value** with status `outcome` | *(no option equivalent)*: reported effects, closest to option → driver consequences | Consequences | — | **Excluded** from option matching; matched against drivers/impacts instead (§5.1 M5) |
| **Decision status** (`accepted` / `rejected` / `outcome`) | Not modeled. Papers occasionally discuss discouraged options in prose | Part of the action/consequence reading | — | Not compared. Only used to route values (options vs. outcomes) |
| **Driver** (planned `Driver`, §8 P7; today only prompt-level "quality-attribute anchoring") | **Decision driver** / **force** (C1 Table 2: "Decision Drivers (Forces)"; C2: CamelCase italics, e.g. *SafetyConstraints*) | Causal / intervening conditions, context | Properties of principal interest (quality attributes) | Unit of **driver-level** matching |
| **Impact** (planned `Value.impacts[{driver_id, effect}]`) | Option → driver relation (the positive/negative influence of an option on a force) | Consequences | — | **Impact agreement** on matched (option, driver) pairs |
| **Relation** (dimension → dimension). Today: `precondition`, `consequence`, `co_occurring`, `constrains`. **After §8 P17**: `enables`, `constrains`, `complements` + optional free-text `label` | **Decision relations** as UML stereotypes: «Enables», «Constrains», «Mandatory Next», «Feeds Into Via Trigger», «Can Be Combined With», «Complements», «Complements But Limited By», … (study-specific, from the authors' ADD-modeling practice in CodeableModels, **not** Straussian constructs) | Relations between categories (paradigm model) | Dependencies between dimensions ("dimensions aren't independent") | After P17, Delve's types **are** the scoring classes; only the GT side is mapped (§4.2.3) |
| *(none; option-level relations are future work, §8 P16)* | Option-level relations (e.g. options that can be combined) | Relations between subcategories | Infeasible / meaningless combinations | Not compared in this paper |

#### 4.2.2 Process and provenance elements (reported, not matched)

| Delve term (code) | Papers' term | Straussian GT | Use in the evaluation |
|---|---|---|---|
| **Document / passage** (`Doc`; planned passage id `"{source_id}#p{k}"` with `source_id`) | **Knowledge source** (C1/C2: s1–s29; practitioner articles, blogs, videos, forums) | Data / incidents | Passages always map back to a source id, so provenance can be compared per source |
| **Open code** (`OpenCode`: label, rationale, status, planned `evidence`, `kind`) | Codes from open coding (not part of the published model; C1's package includes coding data) | Open code / concept | Not matched in the main evaluation; optional step-level analysis for C1 |
| **Supporting documents / evidence** (`Value.supporting_doc_ids`; planned verbatim `evidence`) | **Evidences** (C1 Table 2: "Evidences (from Practitioner sources)"); "grounded in verbatim evidence" (C2) | Grounding | Grounding precision; optional *source overlap*: do Delve and the experts cite the same sources for a matched option? |
| **Use case** (`use_case`) | Research questions and study scope | Research question | Written from the paper's RQs and scope only (B4) |
| **Saturation** (`check_saturation`, streak; planned structural saturation) | **Theoretical saturation** (C2: the last eleven sources confirmed the model) | Theoretical saturation | E5: when Delve stops vs. when the experts report saturation |
| **Source role** (planned, §8 A5) | **Primary / supporting / confirming** sources (C2 Table 1) | Theoretical sampling / saturation | E5 bonus comparison |
| **Memo trail** (`explanations`, §8 P11) | Memos | Memoing | Qualitative only |
| **Selected dimensions** (`select_dimensions`) | The study's **reporting scope** (e.g. C1's article details only a subset of the modeled ADDs) | *Not* selective coding (no core category) | Secondary comparison view only |
| **Persona** (future work) | The analysts (paper authors) | Coder | — (future work) |
| *(no equivalent)* | **Option families** (C2: analytical groupings of options, e.g. *Agent-Internal Signals*) | Subcategories | Metadata only: explains partial or broader matches; not a matching target |
| *(to confirm when converting C1, B1)* | C1's model elements **"considerations"** and **"practices"** (listed next to options in its abstract) | — | Provisional rule, fixed in B1 before any matching: elements a practitioner *chooses* count as options; elements that *motivate* a choice count as drivers. Record the final rule in the benchmark datasheet |
| *(C3 only)* design point / unoccupied combination | — | — | Shaw's design point: one system = one combination of options (E9) |

#### 4.2.3 Relation vocabulary and type map (fixed before any matching)

**Decision (2026-09-26)**: Delve's relations between dimensions are redesigned (§8 P17) as a **small, closed
vocabulary from the ADD-modeling literature**. It is deliberately not a copy of either study's
stereotypes:
- copying them would look like fitting the output to the benchmark;
- the stereotype sets are open-ended and differ per study;
- fine types are hard for an LLM to label reliably.

The three Delve types are also the **scoring classes**, so only the GT side needs a mapping, done once per
study in B1.

| Delve type (after P17) | Meaning (A → B) | GT stereotypes mapped to it (C1/C2) | Replaces (Delve today) |
|---|---|---|---|
| `enables` | Deciding A opens up or requires deciding B; A comes first | «Enables», «Mandatory Next», «Feeds Into Via Trigger» | `precondition` (**direction flipped**: today `A → B precondition` means B comes before A) and `consequence` |
| `constrains` | A's choice restricts the options available on B | «Constrains» | `constrains` (unchanged) |
| `complements` | A and B are typically decided together or reinforce each other; undirected | «Can Be Combined With», «Complements», «Complements But Limited By» | `co_occurring` |

- **Free-text `label`** (optional): the finer wording an agent wants to express (e.g. "mandatory next",
  "limited by"). Shown in reports; **never scored**.
- **Gate in B1**: list every relation stereotype actually used in both packages. If they all fit the three
  types, adopt the scheme as is. If a frequent stereotype fits none of them, add it as a fourth type before
  any run (and before P17 is frozen). Stereotypes that link **options** rather than decisions are recorded
  but not scored (option-level relations are future work, P16).
- **Direction**: both sides use "A → B" as "A first / A acts on B". The GT mapping preserves the direction of
  each stereotype as drawn in the UML. `complements` is compared undirected.

#### 4.2.4 Terminology pitfalls to state explicitly in the paper

1. **"Decision" means different things.** In the papers, a *decision* is the whole ADD (= a Delve
   **dimension**). Delve's code and prompts sometimes call a **value** "a decision" (e.g. the `Value`
   docstring "a consolidated decision/value within one dimension"; "decision status"). In the paper, use
   *decision* only for ADDs/dimensions and *option* for values. Consider aligning the docstrings and prompts
   later (not needed for the experiments).
2. **"Dimension" means different things.** In classic GT, a *dimension* is the range of a property within a
   category. In Shaw and Delve, it is a design-space axis (= an ADD).
3. **"Consequence" appears three times** in today's Delve: a relation type (dimension → dimension), the
   Straussian paradigm element (≈ option → driver impacts), and Delve's `outcome` status (a reported
   effect). P17 removes the relation type (folded into `enables`), so in the paper *consequence* only means
   the Straussian element, operationalized as impacts. `outcome` values are compared only through drivers
   and impacts.
5. **Relation stereotypes are not Straussian.** The papers' «Enables», «Constrains», … come from ADD
   modeling (CodeableModels), not from grounded theory. The paper should present Delve's relation types as
   ADD-modeling vocabulary, and drivers/impacts as its Straussian paradigm-model elements.
4. **Drivers are not dimensions.** A Delve dimension named after a quality attribute (e.g. "Latency
   Tolerance") is a sign of a driver promoted to a decision. The matcher checks such dimensions against GT
   drivers as well (§5.1 M4), and they count as a granularity finding, not a hit.

#### 4.2.5 Ground-truth structure and comparison levels (worked out on C2)

The papers present more levels than their machine-readable models contain. Only some levels are matched.

| Level in the paper (C2) | Count | What it is | Delve equivalent | Compared? |
|---|---|---|---|---|
| **Layers** (Fig. 2 boxes: Safe Exploration, Detection, Reward Hacking) | 3 | Presentation groupings of ADDs | none (Delve is flat) | No (optional sanity check, level 6) |
| **ADDs** (e.g. "Reward Degradation Test Statistic Selection") | 7 | A decision point: one question requiring a choice | **dimension** | Yes, primary |
| **Option families** (italic in the prose, e.g. *Agent-Internal Signals*) | a few | Analytical groupings of options, only in the paper text; they can span ADDs | none | No; used to explain partial matches |
| **Decision options** (bold CamelCase, e.g. *CUSUMSequentialTest*) | 62 in the model | Candidate decisions | **value** (accepted / rejected / mixed) | Yes, primary |
| **Decision drivers / forces** (e.g. *SafetyConstraints*) with `+`/`-` impacts on options | 43 in the model | Forces that favour or disfavour options | drivers and impacts (§8 P7); until then Delve's `outcome` values are the closest counterpart | Yes, secondary |
| **ADD relations** («Constrains», «Mandatory Next», «Feeds Into Via Trigger», …) | 6 links | Dependencies between decisions | relations (`enables` / `constrains` / `complements`, §8 P17) | Yes, secondary |

**The machine-readable model is flat** (`replication_package/src/model/model.py`, CodeableModels):
- `CClass(decision, …)` for the 7 ADDs;
- options linked directly via `add_decision_option_link`;
- forces linked to options with `+`/`-` stereotypes;
- typed `next decision` links between ADDs.

It has no layers and no families. It is the **model view** of the ground truth; the paper's own reporting
is the **paper view** (§4.1). Both are used.

**Counts differ between paper and model** (report in the paper):
- Paper Table 2 lists 57 options (ADD 2: 16, ADD 6: 9); the model has 62 (ADD 2: 15, ADD 6: 15).
- The paper quotes 59/72 drivers; the model defines 43 forces.

**Comparison levels**, from most to least important (metrics in §5.1, M3–M7):
1. **Decision ↔ dimension, option ↔ value**: options are matched across the whole model first; decisions are then aligned mainly through shared options. Lenient alignment credits granularity differences:
   - **split**: Delve divides one ADD into several dimensions (e.g. ADD 2's 15 signals into dimensions resembling the paper's own families);
   - **merge**: one Delve dimension spans two ADDs.
2. **Option recall regardless of dimension**: how many of the 62 options Delve found anywhere, plus the placement-aware variant (the option also sits under the aligned dimension). The most robust metric against granularity differences.
3. **Structure agreement**: over matched options, do Delve and the experts group them into decisions the same way (Adjusted Rand Index, naming-independent)?
4. **Drivers and impacts**: until P7, driver-mention recall (expert forces found among Delve's outcome values or descriptions, labelled as weaker); with P7, driver matching and `+`/`-` impact agreement.
5. **Relations**: for aligned decision pairs, a Delve relation of the same coarse type (§4.2.3).
6. **Layer coverage** (optional sanity check, not a reported result): do Delve's dimensions cover all 3 layers?

**Note for the paper's wording:** some ADDs are "select several" decisions. ADD 2 (which signals to monitor) and ADD 6 (detection strategy) are realized as a *set* of options. For them, candidate decisions are combinable options rather than mutually exclusive alternatives. Matching is unaffected, but the paper should not describe every decision point as "pick exactly one".

### 4.3 Construction steps (see §8 items B1–B4)

1. Download packages; convert the CodeableModels ADD models into normalized JSON (model view), transcribe
   what the paper reports into the same schema (paper view), and record the crosswalk between them (§8 B1).
2. Re-collect every source (archived URLs, Wayback for dead links); log recovery coverage (B2).
3. Segment sources into passages with `source_id` provenance (B3 + P1).
4. Write each study's **use case** from its stated RQs and scope, never from its results (B4).
5. Freeze the benchmark (SHA-256 manifest) before any Delve run.

### 4.4 Case study without ground truth: Cursor "Git at any scale" (C3)

**Why it is in the paper**: a different genre from C1/C2 (one engineering article plus a few official
background sources, rather than 29 gray-literature sources). It is also a close analogue of **Shaw's
original setting**: several organizations solved the same problem (hosting Git at scale) in different ways:
- GitHub: filesystem distribution, then Spokes (three-phase-commit replication);
- Google: JGit on a distributed key-value store;
- Microsoft: GVFS/Scalar, Azure DevOps hybrid store;
- Cursor: Continuity (write-ahead log in S3), later Origin.

Each system should appear as a **distinct point** in the mined design space. This lets the paper show the
artifact the way Shaw intended (her Table 1: teams × dimensions).

**Corpus caveat**: the existing corpus (`cursor_git_at_scale_documents.json`) is **16 paraphrased
documents** written from the article and pre-organized by lens (context, decisions, tradeoffs,
alternatives, lessons, evolution). That pre-structuring helps any system. Plan:
- **C3-raw (primary)**: segment the original article and the background sources listed in `references.md`
  into passages with P1, the same preparation as C1/C2 (§8 B6);
- **C3-curated (sensitivity)**: the existing 16-document corpus; compare the two design spaces with
  `compare_taxonomies` to quantify how much corpus preparation shapes the result.

**Evaluation without ground truth** (§9 E9):
1. **Expert assessment**: 2–3 raters (at least one with distributed-systems/infra experience) rate each
   dimension for validity, orthogonality, and usefulness to an architect facing the same problem, and each
   value for correctness against the article. They also list missing decisions. Report Likert
   distributions and inter-rater agreement.
2. **Point placement (Shaw's Table 1)**: the authors map passages to the system they describe (6–7
   systems, a cheap manual step done before seeing any Delve output). Aggregating `label_documents` output
   per system gives a **system × dimension matrix**. Check that the systems are distinguishable, and
   whether the unoccupied combinations are meaningful.
3. **Traceability**: every value's evidence quotes point to article passages (hallucinated-evidence rate,
   as in C1/C2).
4. **Stability**: cross-seed agreement, as in E6.
5. **Optional silver reference**: before seeing any output, one author writes a short list of the decisions
   the article discusses explicitly. Report its recall as *indicative only*, clearly labeled as
   author-produced rather than an expert GT study.

### 4.5 Stretch case C4: Lane's user-interface design space

**What was checked (2026-09-26)**: TR-22 (<https://www.cs.cmu.edu/~Compose/CMU-SEI-90-TR-22.pdf>, 63 pp.)
and the companion TR-18 (<https://www.cs.cmu.edu/~Compose/CMU-SEI-90-TR-18.pdf>, 38 pp.) are both online.
Shaw (2012) only *cites* Lane's thesis as an example of design spaces; the space itself is in these reports.

**What the ground truth would be** (all in TR-22):
- **Appendix A**:
  - **25 functional dimensions** (requirements; 3–5 alternatives each), grouped under headings (External
    Requirements → Application Characteristics / User Needs / I/O Devices / Computer System Environment;
    Basic Interactive Behavior; Practical Considerations);
  - **19 structural dimensions** (architecture choices, e.g. *Application interface abstraction level*
    with six alternatives from *Monolithic program* to *Extensible interaction manager*), grouped under
    Division of Functions and Knowledge / Representation of Information / Control Flow, Communication,
    and Synchronization.
  - The headings are groupings only (Shaw's "substructure"), so the space is **flat**, as Delve requires.
- **Appendix B (design rules)**: for each structural dimension, the "considerations that may favor or
  disfavor each alternative", expressed in terms of functional requirements.
- **§2.2.1**: a ranking of the 10 functional dimensions with the most structural influence.

**Mapping to Delve's vocabulary** (extends §4.2):

| Lane | Delve | Note |
|---|---|---|
| Structural dimension + alternatives | Dimension + values (decision + options) | Primary matching target |
| Functional dimension (+ its levels) | Driver | Lane's drivers have **levels** (e.g. *Command execution time*: short / intermediate / long). Match at driver level; levels are descriptive |
| Appendix B favor/disfavor considerations | Impacts (option ↔ driver, +/−) | Lane's rules depend on the driver's *level* ("long execution time favors multiple threads"); Delve impacts do not. Score sign agreement at (option, driver) level; report level-conditioned rules qualitatively |
| Grouping headings | — (dimension name/description context) | Not matched |
| Lane's relations between dimensions | Few are explicit (some "omitted dimensions" are attached to key ones) | Relation metrics likely n/a |

**What makes it attractive**: classic and flat; unusually **driver-rich** (a strong test of P7); and the
functional/structural split mirrors Delve's drivers vs. decisions.

**What makes it risky** (why it is a stretch goal):
1. **The sources are not in the reports.** The space came from "an extensive survey of existing user
   interface systems" in Lane's thesis (CMU-CS-90-101, 1990), which is **not** at the analogous
   cs.cmu.edu URL. The list of surveyed systems, and therefore the corpus, must come from the thesis. The
   corpus would be 1980s papers and manuals on UIMSs, toolkits and window systems (TR-22 cites e.g. the X
   Window System).
2. **Point-level ground truth is thin.** TR-18's validation used six systems described by their own
   designers, but they are unnamed except *cT* (a worked example with a partial classification). A full
   system × dimension table, if it exists, would be in the thesis.
3. **Method mismatch.** Lane built the space by expert classification of systems, not by grounded theory.
   Frame C4 as *reconstructing a classic expert design space from the material it was built on*.
4. **Old, partly scanned texts**: OCR and cleanup effort, and some manuals are unobtainable. Only URLs and
   scripts can be released, not the texts.

**Go/no-go (by 2026-10-01)**:
- **Go** if all three hold: (a) the thesis is obtained (CMU library / KiltHub / DTIC / interlibrary
  loan); (b) it lists the surveyed systems with references; (c) ≥ 70% of those system descriptions can be
  retrieved as text.
- **No-go**: C4 goes to future work (a natural centerpiece for a journal extension), and the paper only
  mentions it.
- **Fallback that is not worth it for the paper**: running Delve over modern UI-framework documentation
  and using Lane's space only as a reference. The sources would differ, so it would not be a
  reconstruction.

**If go**: reuse the §5.1 matching protocol (structural dimensions as decisions; functional dimensions as
drivers). Add **driver recall** as a headline metric for C4, and, if the thesis has a system
classification, **placement accuracy** (does Delve's labeling put each surveyed system at Lane's value?).
Tune nothing on C4.

---

## 5. Metrics and validity

### 5.1 Fidelity (RQ1/RQ2): matching protocol

Goal: score any system's output (Delve, baselines, ablations) against the expert ADD models of C1 and C2,
in **both ground-truth views** (paper view and model view, §4.1), with **one** procedure. The procedure is fixed before any C1/C2 output is inspected, validated against a
human-made gold alignment, and applied identically to every system.

#### M0 — Pre-registration

Commit the following to the repository **before** the first C1/C2 run:
- the comparison view (§4.2.1) and the two ground-truth views with their crosswalk (§4.1);
- the status routing (accepted/rejected → options; outcome → drivers/impacts);
- the relation vocabulary and the GT type map (§4.2.3);
- the text serialization (M1) and the judge prompt (M3);
- the metric definitions (M7);
- the calibration procedure (M9).

Any later change is logged as a deviation in the replication package.

#### M1 — Normalize every output to one schema

- Every system's output is converted into the same JSON shape as the GT (§4.3, B1):
  `decisions[] → options[] → impacts[]`, `drivers[]`, `relations[]`.
- **Ground truth in two views**: `gt_paper.json` (as reported in the paper) and `gt_model.json` (full
  replication-package model), sharing element ids. A crosswalk marks each element `paper+model`,
  `model only` or `paper only`.
- **Adapters**:
  - **Delve**: dimensions → decisions; accepted/rejected values → options; outcome values → the
    `outcomes[]` list; `Driver` / `impacts` / `relations` as is.
  - **L1 long-context LLM**: already emits this schema.
  - **L2 BERTopic**: topics → options; topic groups (hierarchy) → decisions; no drivers or relations.
    Those metrics are reported as n/a, not as 0.
  - **L3 TnT-style**: the Delve adapter.
- **Text serialization** used for embeddings and the judge:
  - decision: `"<name>: <description>"`;
  - option: `"<decision name> › <option name>: <description>"`;
  - driver: `"<name>: <description>"`.
  CamelCase names are split into words ("ConservativePolicyUpdates" → "Conservative policy updates").

#### M2 — Enrich the ground truth (once, before any output is seen)

GT options and drivers are often bare CamelCase names. Two authors write a **one-sentence description**
for each element of **both views** (the union, so a `paper+model` element has one shared description),
taken from the paper's text or the package's evidence, not from memory, and cross-check each other's. The enriched GT is frozen with the benchmark (SHA-256 manifest). The same enrichment serves all
systems, so it cannot favour one.

#### M3 — Option matching (global, across decisions)

Every system option is compared with **every** GT option, not only with options under an already-aligned
decision. A correct option filed under a different dimension should count as *found*, and its placement is
scored separately (M7).

1. **Candidates**: embedding similarity (cosine on L2-normalized vectors, the same embedding model for all
   systems); keep the top-5 candidates per element in both directions.
2. **Three bands** (thresholds from M9):
   - similarity ≥ τ_high → auto-label `same`;
   - similarity < τ_low → auto-label `different`;
   - in between → **judge**.
3. **Judge**: a model from a *different family* than the generator. It is blind to which system produced
   the item, and pair order is randomized. It gets both serialized items plus their parent decision names,
   and must answer with exactly one graded label:
   - `same`: the same design option;
   - `broader`: the system item covers this GT option and more (e.g. it merges two GT options);
   - `narrower`: the system item is a more specific case of the GT option;
   - `related`: same topic, but a different option;
   - `different`.
4. The result is a **bipartite option-alignment graph** with labeled edges. One system option can match
   several GT options (`broader`) and vice versa (`narrower`).

#### M4 — Decision alignment (derived mainly from option content)

- **Score** for each (system decision *d*, GT decision *a*):
  `s(d,a) = α · overlap(d,a) + (1 − α) · textsim(d,a)`, where `overlap` is the share of *d*'s matched
  options (`same` / `broader` / `narrower`) whose GT counterparts belong to *a*, and `textsim` is the
  embedding similarity of the serialized decisions. Borderline decision pairs go to the judge with the same
  label set.
- **Strict alignment**: a one-to-one assignment (Hungarian, `scipy.optimize.linear_sum_assignment`) on
  `s`, with a minimum score θ_strict.
- **Lenient alignment**: link *d* to every *a* with `overlap(d,a) ≥ θ_share` (e.g. ≥ 30% of *d*'s matched
  options) or a judge label `same` / `broader` / `narrower`. Each GT decision is then classified:
  - **equivalent** (1:1);
  - **merged** (one system decision covers several GT decisions);
  - **split** (one GT decision spread over several system decisions);
  - **partial** (covered only by a `related` / `narrower` share);
  - **missed**.
- **Driver-as-decision check** (pitfall 4, §4.2.4): unaligned system decisions are also compared against
  GT drivers. Hits are reported as "driver promoted to decision".

#### M5 — Driver and impact matching

- **Drivers**: as in M3, restricted to drivers on both sides. Delve `outcome` values are added to the
  system side as extra driver-like evidence, reported separately.
- **Impacts**: for every matched (option, driver) pair on both sides, compare the effect:
  - exact agreement: + = +, − = −;
  - lenient agreement: `mixed` is compatible with either sign.
  Report agreement rate and coverage (the share of GT impacts whose option **and** driver were both
  matched).
- Until P7 lands, the only measurable signal is **driver mention recall**: does a GT driver appear in any
  system dimension or value description (via the judge)? It is labeled as weaker than driver matching.

#### M6 — Relation matching

- The GT side is mapped once to Delve's three types (§4.2.3); system relations are already in that
  vocabulary.
- **Other systems**:
  - L1 (long-context) is prompted with the same three types and definitions;
  - L3 (TnT-style) is Delve with the same schema;
  - BERTopic has no relations (n/a);
  - old-vocabulary outputs (e.g. earlier example runs) are converted by the same compatibility mapping as
    P17.
- A GT relation (A, B, type) is **recovered** if both endpoints are aligned (strict alignment; lenient
  reported too) and the system has a relation between the aligned decisions with:
  - (i) any type → *type-agnostic*;
  - (ii) the same type → *type-aware*;
  - (iii) the same type and direction → *direction-aware* (`complements` is undirected).
- The free-text `label` is not scored. Optionally report how often it paraphrases the GT's fine
  stereotype (judge), as a descriptive statistic only.

#### M7 — Metrics (exact definitions)

Let G_o be the GT options, S_o the system options (outcome values excluded), and similarly for decisions
(G_d, S_d), drivers and relations.

| Metric | Definition |
|---|---|
| Option recall | \|{g ∈ G_o : ∃ edge (s, g) labeled same/broader/narrower}\| / \|G_o\| |
| Option recall, placement-aware | as above, but s's decision is aligned (lenient) with g's GT decision |
| Option precision (raw) | \|{s ∈ S_o : ∃ edge labeled same/broader/narrower}\| / \|S_o\| |
| Option precision (adjusted) | (matched + unmatched rated *valid-but-absent* or *different granularity* in M8) / \|S_o\| |
| Exact-option recall | as option recall, counting only `same` edges (the strictest variant) |
| Decision P/R/F1, strict | from the one-to-one alignment |
| Decision recall, lenient | share of GT decisions that are equivalent, merged or split |
| Granularity profile | counts of equivalent / merged / split / partial / missed GT decisions |
| Grouping agreement | Adjusted Rand Index between the GT decision partition and the system decision partition, over matched options only (naming-independent structure agreement) |
| Driver P/R/F1 | as options, over drivers |
| Impact agreement | exact and lenient agreement rate + coverage (M5) |
| Relation recall / precision | type-agnostic, type-aware, direction-aware (M6) |
| "Related" rate | share of GT options whose best edge is only `related` (near misses; reported, never counted as hits) |

**Two views.** Every metric is computed per study (C1, C2) **and per ground-truth view** (paper, model), as
mean ± sd over seeds. Matching (M3–M6) runs once against the union of both views; each view's metrics are
then computed from that one alignment:
- **Recall** in a view counts only that view's elements.
- **Precision in the paper view** does not count as wrong a system item that matches a `model only` element:
  it is correct, just not reported in the paper. Such items are excluded from the paper-view precision
  denominator, and their number is reported.
- `paper only` elements (reported in the paper but absent from the model) count only in the paper view.

Report the two views side by side, plus the share of each system's matches that fall in `model only`
elements (how much a system finds beyond what the paper reports).

#### M8 — Review of unmatched system items (adjusted precision)

- 2–3 raters label each unmatched system option and decision as one of:
  - *valid but absent from GT*;
  - *different granularity of a GT item* (should have matched: a matcher miss);
  - *out of the study's scope*;
  - *invalid* (unsupported or wrong).
- **Blinding**: raters do not know which system produced an item; items from all systems are pooled and
  shuffled. About 10% already-matched items are mixed in as attention checks.
- Report inter-rater agreement (Fleiss' κ), then majority labels. Matcher misses feed back into the matcher
  validation (M9), not into adjusted precision.

#### M9 — Human gold alignment and matcher validation

1. **Gold alignment**: for **seed 1** of (a) full Delve and (b) the long-context baseline L1, per study, two
   authors independently align the output with the GT (the union of both views) at option level (M3 labels)
   and decision level (M4 classes), in a spreadsheet generated by the tooling. Then they reconcile disagreements. Including L1
   ensures the matcher is validated on a competitor's output, not only on Delve's.
   Rough size: ~50–70 GT options × ~50–80 system options, reduced to top-5 candidates per item, so a few
   hours per study and system.
2. **Human–human agreement**: Cohen's κ on option labels and decision classes, before reconciliation.
3. **Cross-fitted calibration**: fit τ_low, τ_high, α, θ_strict and θ_share on **C1's** gold and apply
   them to **C2's** runs; fit them on **C2's** gold and apply them to **C1's** runs. No threshold is ever
   fitted on the study it scores.
4. **Matcher validity**: report matcher vs. gold on the held-out study (option-edge precision/recall,
   κ on labels, decision-class accuracy). The acceptance target is agreement close to the human–human κ.
   If it falls clearly short, report the gold (manual) numbers for seed 1 as the primary result, and the
   matcher numbers as supporting evidence for the remaining seeds and systems.

#### M10 — Fairness rules

- The same view rules, serialization, embedding model, judge, prompt and thresholds for every system.
- The judge is blind to the system; pair order is randomized; judge calls are cached, so reruns are
  deterministic.
- Metrics a system cannot produce by design (e.g. drivers for BERTopic) are reported as n/a.

#### M11 — Outputs per scored run

- `match.json`: every candidate pair with similarity, label, and label source (`auto` / `judge` / `human`);
- `alignment.csv`: a human-readable spreadsheet for inspection;
- `metrics.json`: all M7 metrics.

`experiments/analyze.py` (A4) aggregates these into Tables 3–5 and Fig. 4.

#### M12 — Minimum viable fallback (if time runs short)

Skip the automatic matcher. Do M1, M2, M9 steps 1–2 (manual gold alignment) for seed 1 of each system, and
compute M7 from the gold alignments alone. Stability over seeds (E6) is then reported with
`compare_taxonomies`, without GT.

#### Illustration (hypothetical, for exposition only; not real outputs or GT content)

A Delve dimension *"Drift Detection Test"* with values *"Page-Hinkley test"* and *"CUSUM on episode
return"* could align with C2's *ADD4 Reward Degradation Test Statistic Selection*:
- both values match GT options (`same`), so `overlap` = 1.0 and the pair is *equivalent*.

A second Delve dimension *"Alert Threshold Tuning"* could then partially overlap ADD4 and fully overlap
*ADD5 False Alarm Rate Control Method*:
- it aligns strictly with ADD5;
- the lenient alignment records it as a split contributor to ADD4.

### 5.1b Other fidelity measures

- **Grounding precision**: for a stratified sample of values, does the cited passage/evidence quote
  actually support the value? Judge plus human check. Also the **hallucinated-evidence rate**: evidence
  quotes that are not substrings of their passage (computed exactly, no LLM).
- **Source overlap** (optional): for matched options, the Jaccard overlap between the sources Delve cites and
  the sources the experts list as evidence.
- **Intrinsic scoreboard** (existing GEval criteria), reported as a secondary signal only.

### 5.2 Stability and cost (RQ4)

- 5 seeds per configuration: `compare_taxonomies` agreement, standard deviation of F1, Jaccard of matched
  GT elements across seeds.
- Tokens, $, and wall-clock per study (from `TokenTracker` and the run metrics in the saved JSON). Contrast
  qualitatively with the expert effort reported in the source studies.

### 5.3 Statistics

- Report mean ± sd over seeds, per study, plus the pooled value.
- Report **per study** (C1, C2) first; pool only as a summary. With 2 GT studies × 5 seeds = 10 paired
  observations, frame results as **estimation** (effect sizes such as Cliff's δ, with bootstrap CIs over
  seeds), not as significance-hunting. Wilcoxon signed-rank only as a secondary indication.
- If a comparison is decisive for a claim (Delve vs. long-context LLM), raise the seeds for those two
  configurations to 10.

### 5.4 Validity safeguards

- **Judge from a different model family** than the generator (needs §8 P9).
- **Matcher calibration**: two authors independently label ~100 alignment pairs; report Cohen's κ
  (human–human and human–matcher).
- **Contamination probe**: ask the generator for each ADD model *without sources* and score it with the
  same metrics (§9 E8).
- **Pinned models, seeds and cached outputs**; configs committed; full replication package.
- **Budget-matched comparisons** whenever a variant uses more LLM calls.

### 5.5 Threats to validity (to write up)

- **Construct**: GT models reflect analyst choices, not a unique truth (mitigated by expert validity of
  unmatched items); matcher errors (mitigated by κ).
- **Internal**: contamination; prompt sensitivity; judge bias; use-case phrasing.
- **External**: two GT studies from one research group; the ADD genre; English gray literature; link rot.
  C3 (a different genre, no GT) partially addresses generality.
- **Reliability**: LLM non-determinism (seeds, multiple runs, released outputs).

---

## 6. Agentic framing

### 6.1 Roles (reframing, backed by ablations)

Four agents (decided 2026-10-02), each a role grouping consecutive LangGraph nodes with one
responsibility and one permission on the shared theory:

> **Coder** (open coding: writes codes) → **Taxonomist** (axial coding and final revision: edits the
> theory through tools) ⇄ **Critic** (judges drafts, feeds back issues and uncovered concepts, decides
> saturation, assesses the final view: reads and judges only) → **Integrator** (selective coding:
> consolidates, delimits and validates the theory)

| Agent | Nodes |
|---|---|
| Coder | `open_code_minibatch` |
| Taxonomist | `generate_taxonomy`, `update_taxonomy`, `review_taxonomy` |
| Critic | `evaluate_taxonomy`, `check_saturation` (+ `should_review`), `evaluate_taxonomy_final` |
| Integrator | `consolidate_values`, `select_dimensions`, `label_documents` |

There is a single Coder; persona coders are future work (§6.2). External user feedback is an input, not an
agent. Ablations are per mechanism, not per agent (RQ3), so the framing is evidenced rather than asserted.

The full agent model (responsibilities, grounded-theory phases, permissions, autonomy levels, coding
operations as tools, Mermaid workflow diagram, storyline) is in
`docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md` ("The agentic model of the pipeline").

### 6.2 Multi-persona coder agents — out of scope (future work, decided 2026-10-02)

Not part of the paper: open coding uses a single coder agent. The design below is kept for future work.

Rationale: GT triangulation via multiple coders and theoretical sensitivity. The track explicitly lists
multi-agent workflows with coordination.

**Scope (if built)**: personas apply to **open coding only**. The change is local and needs **no change to
`graph.py`** (implementation in §8 P8):
- add a `{persona}` slot to `prompts/open_coding.md` (empty by default, so a config without personas
  produces exactly today's prompt);
- build one open-coding chain per persona in `nodes/open_coder.py::_setup_open_coding_chain`;
- fan out persona × passage inside `open_code_minibatch` (it already runs `asyncio.gather` with a
  semaphore over documents);
- record a `persona` field on `OpenCode` so every code stays attributable.

All persona codes for a minibatch flow into the single taxonomist as today. The taxonomist, value
consolidation (and P5 constant comparison) absorb the synonyms different personas produce for the same
concept. Cost multiplies by N at the open-coding stage only, which uses the fast model.

**Persona sources**, from most to least defensible:

1. **Framework-based lenses**: ISO 25010 characteristics grouped into 3–4 lenses, Rozanski & Woods
   viewpoints/perspectives, or stakeholder roles (architect, SRE/ops, security, developer). Caveat: if the
   GT drivers use ISO 25010 vocabulary, disclose the shared vocabulary.
2. **GT-tradition personas**: Glaserian (emergent, in-vivo codes), Straussian (paradigm model), Charmaz
   (gerund/process codes). They differ in procedure, not role-play.
3. **Model-diversity coders**: the same prompt on different model families (an inter-coder-reliability
   analogue), via the optional per-persona `model` override.
4. **Persona-planner agent**: proposes N lenses from the use case and a sample of documents. Most agentic,
   least controlled.

**Prompt discipline**: the base prompt is identical for all personas; only a structured block varies:

```yaml
personas:
  - id: reliability
    lens: "Operational reliability and failure handling of the system."
    attend_to: [failure modes, recovery, monitoring signals, degradation, rollback]
    de_emphasize: [UI concerns, pricing]
    model: null            # optional per-persona model override (enables model-diversity coders)
# Invariant rule appended to every persona block:
# "The lens changes what you notice, not the evidence standard. Code only what the
#  text states; decision-status and evidence rules are unchanged."
```

**Provenance in outputs**: persona ids travel with the open codes. A small post-hoc step (A8) derives, per
value, which personas' codes support it (via `supporting_doc_ids` + open codes). This yields per-persona
contribution statistics and report badges without touching the taxonomy schema.

**Out of scope (future work)**: persona agents at axial coding (one taxonomist per persona plus a
reconciliation node) and at review. Mention them in the paper's future work.

### 6.3 Theoretical sampling agent — out of scope (future work, decided 2026-10-02)

Not part of the paper: the corpus is read in fixed, shuffled minibatches, and the paper states this as an
approximation of grounded theory (threats to validity). Kept as future work: after each saturation check,
an agent would re-rank the *remaining* minibatches by similarity to the reported `uncovered_concepts` and
read the most relevant next (former backlog item P6).

### 6.4 Deferred

A web-searching source-acquisition agent (true theoretical sampling over the open web) breaks
comparability with fixed GT source lists. Mention it as future work.

### 6.5 Exploring a design space (side idea, not in paper scope)

Exporting a run as a queryable graph + wiki with a CLI is analyzed separately in
`docs/DESIGN_SPACE_EXPLORATION.md`. For the paper, at most a one-line tool-support mention, and only if
it is built and used to analyze C1/C2 before the deadline.

---

## 7. Aligning Delve's procedure with Straussian grounded theory

### 7.1 Reference procedure (Strauss & Corbin 1990/1998; Corbin & Strauss 2008/2015)

- **Open coding**: break data into incidents; label concepts; identify their **properties** and
  **dimensions** (ranges of variation, in the GT sense); in-vivo codes; code notes (memos).
- **Axial coding**: relate categories to subcategories through the **paradigm model**: causal conditions →
  phenomenon → context → intervening conditions → action/interaction strategies → consequences.
- **Selective coding**: core category, storyline, integration, validation against data.
- **Throughout**: constant comparison, **theoretical sampling**, theoretical saturation (no new properties,
  dimensions *or relationships*), memos and diagrams, conditional/consequential matrix, theoretical
  sensitivity (sensitizing literature is allowed).
- SE-specific guidance to cite and follow: Stol, Ralph & Fitzgerald (ICSE 2016); ACM SIGSOFT Empirical
  Standards (GT).

**Key observation**: the Zdun-group ADD studies instantiate the paradigm model as *decision = phenomenon,
options = action/interaction strategies, drivers = conditions, option → driver impacts = consequences*.
Making Delve more Straussian therefore **also makes its output directly comparable to the ground truth**.

### 7.2 Gap analysis

| Straussian element | Delve today | Gap | Fix (§8) |
|---|---|---|---|
| Incidents / open coding | Per-document codes over *summaries*; label + rationale + status | No passages, no verbatim evidence, no code typing | P1, P2, P3, P4 |
| Constant comparison | Minibatch-level in update; value merge in consolidation | Open coder does not see the existing codebook | P5 |
| Paradigm model (axial) | Dimension-level `Relation` (types that mix sequencing and consequences) | No drivers/conditions or consequences; relation types collide with paradigm terms | P7 (drivers + impacts), P17 (ADD relation vocabulary) |
| Theoretical sampling | Fixed shuffled minibatches | Absent | Out of scope (future work; P6); stated as an approximation |
| Theoretical saturation | Concept-coverage streak | Ignores properties, relations, drivers | P10 |
| Memoing | `explanations` accumulated in state | Not rendered as a memo trail | P11 |
| Selective coding | `select_dimensions` = relevance filter | No core category or storyline; misleading name | P14 (could) |
| Theoretical sensitivity | `use_case` + QA anchoring in prompt | No explicit sensitizing-concepts input | P15 (could) |
| Source roles | — | Primary / supporting / confirming (as in the Zdun studies) | A5 |
| Multiple coders (triangulation) | Single prompt and model at every stage | No independent coding perspectives | Out of scope (future work: persona coders, P8) |

---

## 8. Implementation backlog (codebase changes)

Conventions:
- Every behavioural change sits behind a **config switch** whose default keeps today's behaviour. This
  keeps the existing examples reproducible and makes each change an ablation.
- Every item ships with unit tests in `tests/unit_tests/`.
- After code changes, run `graphify update .`.

Priority key: **M** = must (before freeze), **S** = should, **C** = could / post-deadline.

### 8.1 Pipeline (P) — `src/taxonomy_generator/`

| ID | Pri | Change | Files | Config switch | Tests | Effort | Serves |
|---|---|---|---|---|---|---|---|
| P1 | M | **Passage segmentation.** Split long documents into passages (paragraph-aware, ~150–400 words, overlap 0). Passage id `"{source_id}#p{k}"`; keep `source_id` on `Doc` | new `nodes/segmenter.py` (or inside `corpus_loader.py`); `state.py::Doc` (+`source_id`); `utils.py::docs_from_dicts` | `ingestion.segment: false`, `ingestion.passage_words: 300` | splitting boundaries, id stability, provenance round-trip | 0.5 d | all RQs |
| P2 | M | **Open-code raw content, not summaries.** `_doc_input` must honour a setting | `nodes/open_coder.py::_doc_input`; `settings.py` / `configuration.py` | `open_coding.input: summary\|content` (study configs use `content`) | input selection | 0.25 d | RQ1 grounding |
| P3 | M | **Verbatim evidence per code.** `OpenCode.evidence: str` (≤ 40 words, verbatim); prompt demands a verbatim quote; post-check marks `evidence_verified` by normalized-substring match against the passage | `schemas.py::OpenCode`; `prompts/open_coding.md`; `nodes/open_coder.py` | `open_coding.require_evidence: false` | substring verifier; schema | 0.5 d | grounding precision, hallucinated-evidence rate |
| P4 | M | **Paradigm-typed codes.** `OpenCode.kind ∈ {decision_option, driver, condition, consequence}`; axial prompts use kinds to build options vs. drivers vs. impacts | `schemas.py`; `prompts/open_coding.md`; `utils.py::format_open_codes_for_docs`; `prompts/taxonomy_generation.md`, `taxonomy_update.md` | `open_coding.paradigm_kinds: false` | schema + prompt-content tests | 0.5 d | RQ1 drivers, RQ3 |
| P5 | M | **Codebook-aware open coding (constant comparison).** Pass the top-K existing code labels (and current dimension/value names) into the open-coding prompt; instruct reuse over invention | `nodes/open_coder.py` (read `state.open_codes`, `state.clusters[-1]`); `prompts/open_coding.md` (+`{codebook}` slot) | `open_coding.codebook_context: false`, `open_coding.codebook_max: 60` | codebook formatting, cap | 0.5 d | stability (RQ4), RQ3 |
| P6 | — | **Out of scope (future work, 2026-10-02).** ~~Theoretical sampling.~~ After `check_saturation`, reorder `state.minibatches[open_code_batch_index:]` by mean embedding similarity between their passages and `uncovered_concepts` (fallback: unchanged order). Log the chosen order | `nodes/saturation_checker.py` (or new node `select_next_batch` between `check_saturation` and `open_code_minibatch` in `graph.py`); `state.py` (+`sampling_log`) | `pipeline.theoretical_sampling: false` | reordering deterministic given embeddings; no-op when saturated | — | — |
| P7 | M | **Drivers and consequences first-class.** `Driver{id, name, description, supporting_doc_ids}` on `TaxonomyOutput` (taxonomy-level list); `Value.impacts: List[{driver_id, effect: positive\|negative\|mixed, rationale}]`. Propagate through generation/update/review prompts, `format_taxonomy`, consolidation (union impacts on merge; conflicting signs → `mixed`), GT report catalog, HTML report, JSON serialization | `schemas.py`; `prompts/taxonomy_generation.md`, `taxonomy_update.md`, `taxonomy_review.md`; `utils.py::format_taxonomy`; `nodes/value_consolidator.py::_merge_group`; `report_renderer.py::render_catalog`; `html_report.py`; `main.py` serializers; `state.py` if drivers are kept outside `clusters` | `taxonomy.drivers: false` | schema; merge-impact union; format/round-trip; report rendering | 2 d (largest item) | RQ1 drivers/impacts, Straussian story |
| P8 | — | **Out of scope (future work, 2026-10-02).** ~~Persona coder agents (open coding only; no `graph.py` change).~~ `personas:` list in settings (id, lens, attend_to, de_emphasize, optional model). `{persona}` slot in `open_coding.md`, empty by default so no personas → byte-identical prompt. `_setup_open_coding_chain` builds one chain per persona (per-persona model via `load_chat_model`). `open_code_minibatch` fans out persona × passage under the existing semaphore, in deterministic persona-id order. `OpenCode.persona: Optional[str]`. Persona ids are **not** shown to the taxonomist (`format_open_codes_for_docs` unchanged) to avoid biasing axial coding. For the budget-matched control: `open_coding.samples_per_doc: 1` (k > 1 = k persona-less codings per passage) | `settings.py` (+`PersonaSettings`); `configuration.py`; `nodes/open_coder.py`; `prompts/open_coding.md`; `schemas.py::OpenCode` | `personas: []`, `open_coding.samples_per_doc: 1` | no personas → identical prompt and one call per passage; N personas → N× calls, each code tagged; deterministic order; per-persona model routing; `samples_per_doc` fan-out | — | — |
| P9 | M | **Provider-agnostic judge.** A deepeval `DeepEvalBaseLLM` wrapper around `utils.load_chat_model`; `consistency.py` adjudication via `load_chat_model` instead of `AsyncOpenAI` | `evaluation/judge.py`, `evaluation/metrics.py::build_metrics`, `evaluation/consistency.py` | `evaluation.judge_model: anthropic/…` etc. | wrapper contract; fallback | 0.5 d | cross-family judge (validity) |
| P10 | S | **Structural saturation.** Compute a round-over-round diff (dimensions/values/drivers/relations added, removed, renamed) between `clusters[-2]` and `clusters[-1]`; saturated only if concept coverage holds **and** diff ≤ threshold | `nodes/saturation_checker.py`; `state.py` (`saturation_history` gains `diff`) | `taxonomy.structural_saturation: false`, `taxonomy.saturation_max_edits: 1` | diff function on fixtures | 0.5 d | Straussian fidelity, E5 |
| P11 | M | **Memo trail.** Render every iteration's `explanations` (and saturation rationales) as an "Evolution of the theory" section in the GT report / HTML report | `report_renderer.py` (new `render_memo_trail`), `html_report.py` | always on | rendering | 0.5 d | Approach figure, qualitative results |
| P12 | M | **Ablation switches** not yet available: (a) `open_coding.enabled: true` (false → axial coding directly on passages/summaries, i.e. TnT-style); (b) `review.enabled: true` (false → `review_taxonomy` passes through); (c) `evaluation.feedback_in_loop: true` (false → scoreboard computed but not injected via `format_feedback`); (d) `open_coding.decision_status: true` (false → status neutralized in prompts and ignored by consolidation) | `graph.py` / routing (`should_generate_or_update`), `nodes/taxonomy_reviewer.py`, `utils.py::format_feedback`, `prompts/*`, `nodes/value_consolidator.py` | as listed | one test per switch verifying pass-through | 1 d | RQ3 |
| P13 | M | **Run provenance.** Persist the resolved config, git SHA, model ids, seed, token/$ totals and wall-clock into the saved taxonomy JSON (extends the existing run-metrics persistence) | `main.py` (serialization), `settings.py` | always on | JSON contains fields | 0.25 d | open science |
| P14 | C | Real selective coding: rename `select_dimensions` → "scoping" in docs/prompts; add core-category nomination + relation centrality + storyline | `nodes/dimension_selector.py`, `schemas.py::SelectionOutput`, `report_renderer.py` | `selection.core_category: false` | — | 1.5 d | future work |
| P15 | C | Sensitizing concepts input (e.g. ISO 25010 list) injected into open/axial coding | `settings.py`, prompts | `taxonomy.sensitizing_concepts: []` | — | 0.5 d | future work |
| P16 | C | Option-level relations (combinable-with / excludes / requires) | `schemas.py`, prompts, report | — | — | 1.5 d | future work |
| P17 | M | **ADD relation vocabulary.** Replace `Relation.type` `Literal["precondition","consequence","co_occurring","constrains"]` with `Literal["enables","constrains","complements"]` plus an optional `label: Optional[str]` (free text, not scored). Rewrite the relation definitions in the generation/update/review prompts (direction: "A → B = A first / A acts on B"; `complements` undirected; assert a relation only when the use case's logic requires it). Update relation formatting and the diagram edge labels. **Backward compatibility**: when loading saved taxonomies, map old types: `precondition` A→B becomes `enables` **B→A** (flipped); `consequence` A→B becomes `enables` A→B; `co_occurring` becomes `complements`; `constrains` stays; the old type is kept in `label`. Update `CONCEPTS.md` (Relation entry). **Gate**: finalize the type list after the B1 inventory of GT stereotypes (a fourth type only if a frequent one fits none) | `schemas.py::Relation`; `prompts/taxonomy_generation.md`, `taxonomy_update.md`, `taxonomy_review.md`; `utils.py::format_taxonomy`, `utils.py::load_seed_taxonomy`; `report_renderer.py::render_diagram`; `html_report.py`; `CONCEPTS.md` | `taxonomy.relation_vocabulary: legacy \| add` (default `add` for the study; `legacy` keeps today's prompts for the old examples) | schema literal; the old→new mapping with direction flip on fixtures; loading an old example taxonomy; prompt-content test for the definitions; diagram labels | 0.5–1 d (do together with P7) | RQ1 relation metrics; removes the direction pitfall |

**Note on P7 and downstream code**: `doc_labeler`, `visualization` and `value_aggregator` read `clusters`.
Adding optional fields (`impacts` defaults to `[]`, drivers stored alongside) must not break them. Add a
regression test that loads an old saved taxonomy JSON.

### 8.2 Benchmark construction (B) — new `benchmark/` directory

| ID | Pri | Deliverable | Notes | Effort |
|---|---|---|---|---|
| B1 | M | `benchmark/gt_convert.py`: CodeableModels (Python) → `benchmark/<study>/gt_model.json` `{decisions[{id,name,description,options[{id,name,impacts[{driver,effect}]}]}], drivers[], relations[{source,target,type}]}`; plus `gt_paper.json` (same schema, transcribed from the paper's text, tables and figures) and `gt_crosswalk.csv` (each element: `paper+model` / `model only` / `paper only`) | For C1 and C2 (and the DT dev set if used). Element ids are shared across the two views. Import the model modules directly if runnable, otherwise parse. Hand-check against the paper tables. Includes **GT enrichment (§5.1 M2)**: one-sentence descriptions for options and drivers, the C1 "considerations/practices" rule (§4.2.2), and the **inventory of relation stereotypes** in both packages with their mapping to Delve's types (§4.2.3; this gates P17), all frozen before any run | 1 d (+0.5 d for M2 enrichment) |
| B2 | M | `benchmark/fetch_sources.py`: download each source URL (fallback: Wayback), extract main text (e.g. `trafilatura`), store `sources/<sid>.txt` + `manifest.json` (url, archive url, retrieval date, sha256, status) | Start on day 1 (link rot is the critical path). Legal note: store only in the private workspace; release URLs + scripts, not full text, if licensing is unclear | 1 d |
| B3 | M | `benchmark/build_corpus.py`: sources → passages (P1) → Delve corpus JSON per study | Same segmentation for all systems (fairness) | 0.25 d |
| B4 | M | `benchmark/<study>/config.yaml` + `use_case.md`: use case from the study's RQs and scope only | Two authors agree on the wording; frozen before runs | 0.25 d |
| B5 | S | Benchmark datasheet (`benchmark/README.md`): provenance, coverage, licensing, known issues (e.g. RL-study count discrepancy, C1 article-vs-package scope) | For the paper's benchmark section | 0.25 d |
| B6 | M | **C3 corpora**: `benchmark/cursor/` with (a) **C3-raw**: the Cursor article + background sources from `examples/cursor-git-at-scale/references.md` fetched by B2 and segmented by P1; (b) **C3-curated**: the existing `cursor_git_at_scale_documents.json`; (c) a use case (reuse or refine `git_at_scale_config.yaml`) | Keep the curated corpus untouched for comparability with the earlier example runs | 0.25 d |
| B7 | M | **C3 system mapping**: `benchmark/cursor/passage_systems.csv`, where authors map each C3-raw passage to the system(s) it describes (GitHub FS, Google JGit/DHT, GitHub Spokes, Microsoft GVFS/Scalar, Azure DevOps hybrid, Cursor Continuity/Origin, general). Done **before** looking at any Delve output. Plus the optional author-written silver decision list | Needed for the system × dimension matrix (E9) | 0.5 d |
| B8 | C (stretch) | **C4 feasibility check**: obtain Lane's thesis (CMU-CS-90-101); extract the list of surveyed systems and references; try retrieving 5 system descriptions and extrapolate; decide go/no-go by 10-01 (§4.5) | TR-22 and TR-18 already downloaded to the session scratchpad; copy into `papers/base/` if C4 goes ahead | 0.25 d |
| B9 | C (stretch) | **C4 benchmark** (only if go): TR-22 Appendix A → `benchmark/lane/gt_model.json` (structural dimensions → decisions/options; functional dimensions → drivers with levels); Appendix B → impacts; fetch/OCR the system sources; passage→system mapping; use case from TR-22 §1 | Same M2 enrichment and freezing rules as C1/C2 | 1.5–2 d |

### 8.3 Evaluation and analysis (A) — `src/taxonomy_generator/evaluation/` + `experiments/`

| ID | Pri | Deliverable | Notes | Effort |
|---|---|---|---|---|
| A1 | M | `evaluation/gt_match.py`: implements the **matching protocol §5.1 M1–M7 and M10–M11**: adapters (Delve, L1, L2, L3) → common schema; CamelCase splitting and serialization; global option matching (embedding bands + graded judge); decision alignment (strict Hungarian via `scipy.optimize.linear_sum_assignment`, lenient classes, driver-as-decision check); driver/impact and relation matching with the §4.2.3 type map; all M7 metrics; `match.json` / `alignment.csv` / `metrics.json` | Reuse `l2_normalize`, `_cross_distances`, and the borderline-judge pattern from `consistency.py`; judge through P9; cache judge calls | 2 d |
| A2 | M | `evaluation/grounding.py`: hallucinated-evidence rate (exact); sampled support check (judge) + export CSV for human check | Needs P3 | 0.5 d |
| A3 | M | `experiments/run_matrix.py`: expands a YAML experiment matrix (study × variant × seed) into runs; skips completed runs (idempotent); writes `experiments/runs/<exp>/<study>/<variant>/seed<k>/` | Uses `graph.ainvoke` directly or `main.py` subprocess; respects rate limits | 1 d |
| A4 | M | `experiments/analyze.py`: collects metrics → tidy CSV → LaTeX tables + matplotlib figures (bootstrap CIs, Wilcoxon, Cliff's δ) | Outputs straight into `paper/figures`, `paper/tables` | 1 d |
| A5 | S | `evaluation/source_roles.py`: primary/supporting/confirming per source from the order in which sources first contributed new decisions/options/drivers (uses `open_codes` + `clusters` history) | Compare with the RL study's Table 1 classes | 0.5 d |
| A6 | M | **Gold-alignment and calibration kit (§5.1 M9)**: generate alignment spreadsheets (top-5 candidates per item) for seed 1 of full Delve and L1 per study; κ scripts (Cohen's for gold, Fleiss' for M8); cross-fitted threshold fitting (C1 → C2, C2 → C1); matcher-vs-gold report. Plus ~60 grounding items for the human grounding check | Two authors, a few hours per study and system | 1 d |
| A7 | S | Expert-rating kit for unmatched items (anonymized, randomized, one sheet per rater) | For adjusted precision | 0.25 d |
| A8 | — | **Out of scope (future work, with P8).** `evaluation/persona_provenance.py`: per value, which personas' codes support it (via `supporting_doc_ids` + `open_codes[*].persona`); per-persona unique GT options (with A1); code-volume and near-duplicate rates; persona agreement per passage (embedding-matched Jaccard of code labels) | For E4 and Fig. 5; post-hoc, no schema change | — |
| A9 | M | `evaluation/placement_matrix.py`: from labeled passages (`label_documents`) + `passage_systems.csv` → system × dimension matrix (the value each system takes per dimension, with evidence counts), plus distinguishability (pairwise system distance) and unoccupied-combination listing. Plus the expert-rating kit for C3 (dimensions and values) | For E9 / Fig. 8 | 0.75 d |

### 8.4 Baselines (L) — new `baselines/` directory

| ID | Pri | Baseline | Implementation notes | Effort |
|---|---|---|---|---|
| L1 | M | **Long-context single prompt** | All passages (or full sources) in one prompt; asks for Delve's JSON schema (decisions, options, drivers, impacts, relations, supporting passage ids). Same generator model as Delve. 5 seeds / temperature | 0.5 d |
| L2 | M | **BERTopic + LLM labels** | Passages → BERTopic (same embedding model as Delve) → topics as candidate options; hierarchical topics / agglomeration of topic embeddings → candidate decisions; LLM names both. Output converted to the same JSON for A1 | 1 d |
| L3 | M | **TnT-LLM-style** | Delve config: `open_coding.enabled: false`, `review.enabled: false`, `consolidate_values: false`, `paradigm_kinds/drivers: false`, summaries on | config only (needs P12) |
| L4 | C | **LLooM** | Run the public package on passages; map concepts to options | 1 d |
| L5 | M | **Contamination probe** | No sources: "Reconstruct the ADD model for <study scope>" → same JSON → A1 | 0.25 d |

### 8.5 Housekeeping (H)

| ID | Pri | Item |
|---|---|---|
| H1 | M | Fix the stale OpenWiki validation note (tests exist) — via source docs, not by editing generated pages |
| H2 | M | `experiments/README.md`: how to reproduce every table and figure |
| H3 | M | Anonymized replication package (anonymous.4open.science): code at the freeze tag, configs, benchmark manifests + GT JSON, all run outputs, analysis scripts |
| H4 | S | Pin dependency versions (lock file) and record model snapshot ids |

### 8.6 Order of work (dependencies)

```
B2 (fetch sources) ─┬─> B3 ─> B4 ──────────────────────────────┐
P1 ─> P2 ─> P3 ─> P4 ─> P5                                     │
P7 (drivers) + P17 (relations) ─────────────┐                  ├─> dry run (1 study) ─> FREEZE ─> E1…E8
P9, P11, P12, P13 ──────────────────────────┤                  │
B1 (GT convert; stereotype inventory gates P17) ─> A1 (matcher) ─> A6 ┘                  │
A3 (harness) ─> L1, L2, L3, L5 ────────────────────────────────┘
B2 + P1 ─> B6 (C3 corpora) ─> B7 (passage→system map) ─> A9 ─> E9   (B6 also feeds the E0 pilots)
P10, A5 (should, only if on schedule); P6, P8/A8/E4 out of scope
```

### 8.7 Progress log

- **2026-10-01: B2 done.** `benchmark/fetch_sources.py`. C1 29/29 sources and C2 27/29 (s5 needs a manual
  save, s10's page is gone); verified against the analysts' memo quotes.
- **2026-10-01: B3 and P1 done (builder-side) and P2 done.**
  - `benchmark/build_corpus.py` writes passage corpora (~300 words, ids `sNN_pKK`) to
    `examples/c1-ml-workflow/` (265 passages) and `examples/c2-rl-monitoring/` (243 passages).
  - P1 is implemented in the corpus builder rather than as a pipeline node; the passage id carries the
    source id.
  - `main.load_corpus_documents` keeps corpus ids.
  - New setting `open_coding.input: summary | content` (default `summary`; the C1/C2 configs use `content`
    with summarization skipped).
- **2026-10-01: first C1/C2 runs, and fixes they prompted.** The runs produced 34 (C1) and 43 (C2)
  dimensions; several had no labeled documents. Fixed:
  - the labeler now classifies against the *selected* taxonomy;
  - it returns a dimension id, which is validated (one retry, then the fallback);
  - dimension and value ids are made unique;
  - **evidence linking** (`nodes/evidence_linker.py`) rebuilds each value's supporting documents
    deterministically from the open codes (before, 77% of C2 passages supported no value);
  - open codes are now saved per run (`*_open_codes_*.json`).

  Labeling stays single-label (option (a)).
- **2026-10-01: fragmentation controls** (all behind settings; enabled in the C1/C2 configs):
  - dimension merging before value consolidation (`nodes/dimension_merger.py`; embedding candidates
    plus an LLM judge on "same design decision"; thresholds calibrated on the C2 run, where
    near-duplicates sit at distance 0.58–0.75);
  - a minimum-support rule at selection (≥ 2 sources, from the new evidence);
  - tolerant saturation (`saturation_min_coverage: 0.9`) and critic feedback that prefers adding
    options to existing dimensions over new ones.
- **B4 drafted:** use cases in `examples/c1-ml-workflow/c1_ml_workflow_config.yaml` and
  `examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml`, still to be agreed by two authors.

---

## 9. Experiment protocol

### 9.1 Fixed settings across experiments

- **Cases**: C1 ML-workflow (GT), C2 RL-monitoring (GT, running example, held out from tuning), C3 Cursor
  git-at-scale (no GT; C3-raw primary, C3-curated sensitivity).
- **Input**: recovered sources → passages (P1), identical for all systems.
- **Models**: one generator family (decide in §12), fast model of the same family; judge from a **different
  family** (P9); one embedding model for everything.
- **Seeds**: 5 per configuration (`pipeline.random_seed` ∈ {1..5}), temperature per provider default.
- **Delve "full" configuration**:
  - `segment: true`, `open_coding.input: content`, `require_evidence: true`, `paradigm_kinds: true`;
  - `codebook_context: true`, `drivers: true`, `evaluation.feedback_in_loop: true`;
  - `consolidate_values: true`, `review.enabled: true`;
  - a single coder agent (personas are future work);
  - `max_num_clusters: null`.
- **Outputs**: every run stores the taxonomy JSON (with P13 provenance), open codes, saturation history,
  scoreboard, and tokens/$.

### 9.2 Experiments

**E0 — Pilot and calibration** (before freeze; not reported as a result)
- Constraint: with only two GT studies, **neither C1 nor C2 may be used for tuning**.
- Pipeline settings (passage size, `batch_size`, saturation threshold) are tuned on **C3-raw** for
  completion, cost and intrinsic scoreboard only (no GT involved), plus the **DT study as a private dev
  set** if its package is usable (decision §12).
- Matcher thresholds: calibrated on human-labeled alignment pairs (A6) with **cross-fitting**: thresholds
  fitted on C1 pairs are applied to C2 and vice versa. Report κ per study.
- Output: frozen settings and thresholds; a cost estimate; a sanity check that runs complete.

**E1 — Fidelity (RQ1)**
- Hypothesis: Delve recovers most expert decisions (ADD recall ≥ ~0.7) and a majority of options, with high
  grounding precision.
- Runs: full Delve × 2 GT studies (C1, C2) × 5 seeds.
- Metrics: §5.1 (strict and lenient), grounding precision, hallucinated-evidence rate, adjusted precision
  (expert ratings, A7).
- Every result is reported in both ground-truth views (paper view, model view), side by side (§5.1 M7).
- Artifacts: **Table 3** (per study and per view: ADD/option/driver/relation P-R-F1, mean ± sd, plus the
  share of matches in `model only` elements); **Fig. 4** (per-ADD
  option recall heat map for the RL study); qualitative box with 2 correct, 1 missed, 1 "valid but absent
  from GT" example.

**E2 — Baselines (RQ2)**
- Hypothesis: Delve > BERTopic on every structural metric; Delve ≥ long-context LLM on option recall and
  clearly better on grounding and stability; Delve > TnT-style.
- Runs: L1, L2, L3 (+L4) × C1, C2 × 5 seeds. L1 and L2 also run once per seed on C3-raw, for the
  qualitative contrast in E9.
- Metrics: as E1 + stability (from E6) + cost.
- Artifacts: **Table 4** (systems × metrics, pooled + per study); **Fig. 1** (motivating example, same
  sources, three outputs).

**E3 — Component ablations (RQ3)**
- Variants (each switches one thing off relative to full):
  - −open coding (P12a);
  - −paradigm kinds (P4);
  - −codebook context (P5);
  - −drivers (P7);
  - −evidence (P3);
  - −judge feedback (P12c);
  - −review (P12b);
  - −consolidation;
  - −early stopping (streak threshold > #batches);
  - −decision status (P12d);
  - plus **"TnT-style" vs. "Straussian"** as the two ends.
- Runs: C1, C2 × 5 seeds per variant (≈ 110 runs). If the budget is tight, 3 seeds, stated plainly.
- Artifacts: **Table 5** (ΔF1 option/ADD/driver, Δgrounding, Δtokens vs. full; effect sizes).

**E4 — Persona coder agents in open coding — out of scope (future work, decided 2026-10-02)**
- Not run for the paper; the design is kept for future work.
- Hypotheses:
  - (H1) persona coders raise option and driver recall compared with a single coder **at equal
    open-coding budget**;
  - (H2) precision after consolidation does not drop (synonym inflation is absorbed);
  - (H3) personas contribute expert options that no persona-less sample finds (a lens effect, not just
    more sampling).
- Variants (C1, C2 × 5 seeds):
  1. single coder (baseline = full configuration);
  2. **budget-matched control**: single coder, `samples_per_doc: 3` (three persona-less codings per
     passage). This isolates "more coding samples" from "different lenses";
  3. 3 framework-based personas (§6.2 source 1);
  4. (optional) 3 model-diversity coders (same prompt, 3 model families);
  5. (stretch) GT-tradition personas.
- Metrics:
  - E1 metrics;
  - code volume and near-duplicate rate before/after consolidation;
  - per-persona unique GT options (A8);
  - noise floor: code overlap between same-prompt samples (variant 2) vs. across personas (variant 3);
  - open-coding cost.
- Guard: persona definitions are written once from the study-independent source, never tuned on GT results.
- Artifacts: **Fig. 5** (UpSet plot of expert options recovered via each persona's codes vs. the
  budget-matched samples); **Table 5b** (variants × recall/precision/cost).

**E5 — Saturation (RQ3c)** (only if P10 lands; the theoretical-sampling variant is out of scope, see §6.3)
- Hypothesis: structural saturation stops later but more completely than concept saturation.
- Measure: recall-vs-passages-read curves; passages read at stop; final recall.
- Artifacts: **Fig. 6** (recall vs. passages consumed, with and without structural saturation; fixed
  shuffled order).
- Bonus: compare Delve's source-role classification (A5) with C2's primary/supporting/confirming labels.

**E6 — Stability and cost (RQ4)**
- Derived from the E1/E2 runs, no extra runs.
- Metrics: cross-seed agreement, F1 sd, Jaccard of recovered GT elements; tokens, $, and wall-clock per study.
- Artifacts: **Table 6** or a panel in Table 4; one sentence contrasting with the expert effort reported.

**E7 — Human-in-the-loop (RQ5, optional)**
- Protocol: for C1 and C2, one expert (not exposed to the GT model) reads the run-1 report (seed 1) and
  writes ≤ 300 words of critique → run 2 with `--taxonomy run1.json --feedback-file critique.md` → ΔF1.
- Control: run 2 without feedback (a seeded re-run) to separate "second pass" from "feedback" effects.
- Optional upper bound: oracle feedback generated from the GT diff, labeled as such.
- Artifacts: small table or paragraph.

**E8 — Contamination probe (validity)**
- L5 × C1, C2 × 5 seeds. Report its F1 next to Delve's. Expected: noticeably higher for C1 (2021) than
  for C2 (2026). If so, C2 carries the fidelity claims and C1 is discussed with this caveat. If both are
  low, contamination is unlikely to explain Delve's results.

**E9 — Case study without ground truth: Cursor git-at-scale (RQ6)**
- Runs: full Delve × C3-raw × 5 seeds; full Delve × C3-curated × 5 seeds; L1 and L2 on C3-raw (from E2).
- Analyses (§4.4):
  1. expert assessment of dimensions and values (validity, orthogonality, usefulness, missing decisions)
     with inter-rater agreement;
  2. system × dimension placement matrix (A9): are the 6–7 systems distinct points, and which unoccupied
     combinations appear?
  3. hallucinated-evidence rate and sampled grounding;
  4. cross-seed stability;
  5. C3-raw vs. C3-curated agreement (sensitivity to corpus preparation);
  6. (optional) recall of the author-written silver decision list, labeled as indicative.
- Also shows the memo trail (P11): how the theory evolved as the Taxonomist read passages and the Critic judged each draft.
- Artifacts: **Fig. 8** (system × dimension matrix, Shaw Table 1 style); short expert-rating summary
  table or paragraph; one qualitative contrast with the long-context and BERTopic outputs.

**E10 — Stretch: Lane's design space (C4)** (only if B8 says go)
- Runs: full Delve × 5 seeds; L1 long-context × 5 seeds; contamination probe (L5).
- Metrics: §5.1 M7 with drivers as a headline metric; impact sign agreement against Appendix B;
  placement accuracy if the thesis has a system classification.
- Artifacts: one row in Table 3 (or a short subsection); otherwise the replication package.

**E11 — Possible: generalization and data stability (RQ4, optional; idea 2026-10-02, not scheduled)**
- Question: do the dimensions inferred in train mode cover unseen sources (not overfitted), and do the same
  dimensions emerge from different sources (data stability, as opposed to the seed stability of E6)?
- Splits are **by source, never by passage** (passages of one article share vocabulary and decisions, so a
  passage split leaks), seeded and stratified by source type; corpus files
  `<case>_corpus_train.json` / `_test.json` with the source lists recorded.
- **Train/test (70/30):** train mode on the train sources, then test mode (`--taxonomy <train run>`) on the
  test sources. Test mode freezes the **selected view** (`pipeline.taxonomy_input_view: auto`, fixed
  2026-10-02), labels each test passage and appends new values; it does not re-run open coding, so it
  measures **coverage of unseen data**, not re-derivation. Overfitting = the **gap** between train
  passages (labeled at the end of the train run) and test passages on: fallback ("Other") rate, test
  sources reaching each dimension, rate of appended values, mean label score; plus the judge's coverage
  criteria on a test sample. Forced single-label labeling can hide misfits, hence label scores, not only
  "Other". Test sets are small (C1 ≈ 9, C2 ≈ 8 sources): report per-dimension results by source counts and,
  budget permitting, repeat with 2–3 splits.
- **Split-half (50/50):** train mode on each half, then the consistency comparison
  (`--evaluate runA.json runB.json`): recurring dimensions are data-stable, one-offs are candidates for
  overfitting to particular sources. Read against E6's cross-seed agreement on the full corpus to separate
  data-driven from pipeline-driven variation.
- Kept separate from E1: training on a subset lowers recall against the ground truth, so fidelity is always
  measured on full-corpus runs.
- To build if scheduled: a source-level split option in `benchmark/build_corpus.py` and a small script
  comparing train vs. test labeling statistics.
- Artifacts: a short table (train vs. test gap per case) and the split-half recurring/one-off counts.

### 9.3 Run budget

| Experiment | Runs (C1, C2 × 5 seeds unless noted) |
|---|---|
| E0 | ~10 (C3-raw pilots; DT dev set if used) |
| E1 | 10 |
| E2 | 30 (+10 LLooM) + 10 on C3-raw |
| E3 | ~110 |
| E4 | — (future work) |
| E5 | ~10 (structural saturation only) |
| E7 | 4 |
| E8 | 10 |
| E9 | 10 (C3-raw + C3-curated) |
| E10 (stretch) | ~15 (C4 if go) |
| E11 (possible) | 8 per split (C1, C2: 1 train + 1 test + 2 split-half trains each); not in the total |
| **Total** | **≈ 205** |

Estimate cost after E0. If the budget is exceeded, cut in this order: E3 to 3 seeds; drop LLooM; drop
C3-curated.

---

## 10. Paper outline and storytelling

### 10.1 Section plan (10 pages)

| § | Section | Pages | Key content | Figures/Tables |
|---|---|---|---|---|
| — | Abstract | — | Problem, approach, benchmark, headline numbers, artifact | — |
| I | Introduction | 1.25 | Motivation (design spaces, ADD models, cost of GT); naive approaches fail (Fig. 1); idea: GT procedure as agent architecture; RQs; contributions | **Fig. 1** motivating example |
| II | Background and related work | 1.0 | Design spaces (Shaw); ADD modeling and GT in SE (Zdun group, Stol et al.); computational/LLM-assisted GT (Nelson; LLM-QDA mapping); taxonomy/topic mining (BERTopic, TnT-LLM, LLooM); LLM agents for SE analysis | Table 1: positioning vs. related approaches |
| III | Delve: a multi-agent Straussian GT workflow | 2.0 | Roles and loops; Straussian step ↔ agent ↔ artifact mapping; paradigm-model schema (decisions, options, drivers, impacts, relations); evidence and memos; HITL | **Fig. 2** architecture; **Table 2** GT step ↔ agent ↔ artifact; **Fig. 3** running-example trace |
| IV | Cases and ADD-Bench | 0.75 | C1/C2 (GT) and C3 (no GT); source recovery, passages, GT conversion (C1 scope), use cases, matching protocol, metrics, calibration (κ, cross-fitted) | Table: case statistics (sources, passages, ADDs/options/drivers) |
| V | Study design | 0.75 | RQs → experiments, systems, baselines, models, seeds, statistics | — |
| VI | Results | 2.75 | RQ1–RQ5 on C1/C2, each with a "finding" box; RQ6: C3 case study (~0.5 page) | **Tables 3–5**, **Figs. 4–6**, **Fig. 8** |
| VII | Discussion | 0.6 | What the agents get right/wrong (granularity, drivers, rare options); agents as instruments in human-led GT; implications for researchers and practitioners; cost | — |
| VIII | Threats to validity | 0.4 | §5.5 | — |
| IX | Conclusion and future work | 0.25 | Theoretical sampling (gap-directed reading order, web-search source acquisition), hierarchical spaces, unoccupied-point exploration, persona coder agents (open and axial coding, review) | — |
| — | Data availability | — | Anonymized package | — |

### 10.2 Figures and tables checklist

| ID | What | Source |
|---|---|---|
| Fig. 1 | Same sources → BERTopic topic vs. long-context output vs. expert ADD (one decision) | E2 outputs + GT |
| Fig. 2 | Architecture: agent roles, loops (judge, saturation critic, human) over the LangGraph | hand-drawn from `graph.py` |
| Fig. 3 | Running-example trace: passage → evidence code (kind) → option → driver impact → GT match | E1 RL-study run |
| Fig. 4 | Per-ADD option-recall heat map (RL study; seeds as columns) | A4 |
| ~~Fig. 5~~ | ~~UpSet plot of persona contributions~~ — future work (E4 out of scope) | — |
| ~~Table 5b~~ | ~~Persona variants~~ — future work (E4 out of scope) | — |
| Fig. 8 | C3: system × dimension matrix (Shaw Table 1 style), unoccupied combinations highlighted | E9 |
| Fig. 6 | Recall vs. passages read (saturation variants) | E5 |
| Table 1 | Positioning vs. related work (unit of analysis, output structure, grounding, GT fidelity, agentic loops) | literature |
| Table 2 | Straussian step ↔ Delve agent ↔ artifact ↔ config switch | §7 + §8 |
| Table 3 | Fidelity per study | E1 |
| Table 4 | Baselines comparison | E2/E6 |
| Table 5 | Ablations | E3 |

### 10.3 Claims ↔ evidence map (nothing goes into the abstract without a row here)

| Claim | Evidence | Fallback wording if weaker than hoped |
|---|---|---|
| Delve reproduces most expert decisions | E1 ADD recall (C2 carries the claim if E8 flags C1) | "recovers a majority of decisions and X% of options" |
| Delve is grounded and traceable | E1 grounding precision, hallucinated-evidence rate | report the rate honestly and discuss failure modes |
| Better than topic mining | E2 vs. BERTopic | — (expected to be robust) |
| Competitive with or better than long-context LLMs | E2 vs. L1, E6 stability | "comparable recall, with higher traceability and stability" |
| The GT-specific agentic components matter | E3 TnT-style vs. Straussian; the largest ablation deltas | name the components that matter, report the null ones |
| Delve works without ground truth, in another genre | E9 expert ratings, placement matrix | "plausible and traceable; experts flagged X" |
| The results are not memorization | E8 | "the RL study (post-cutoff) confirms…" |

### 10.4 Anticipated reviewer objections and prepared answers

| Objection | Answer (and where it is in the paper) |
|---|---|
| "This is a pipeline, not an agent." | Roles with feedback loops and autonomous stopping; ablations show each loop's contribution (Table 5). The track also lists multi-agent workflows |
| "Why not just prompt a long-context model?" | L1 baseline; grounding and stability results; cost at scale; traceability for human-led GT |
| "LLM judge evaluating LLM output." | Cross-family judge, κ calibration, exact hallucinated-evidence metric, expert ratings |
| "Ground truth is one group's opinion." | Expert validity of unmatched items; lenient matching; threat discussed; benchmark open for extension |
| "Contamination." | E8 probe; C1 (2021) vs. C2 (2026) contrast; C2 and C3 likely post-date training cut-offs |
| "Only two ground-truth studies." | Each has 29 sources and hundreds of passages; 5 seeds (10 for the decisive comparison); per-study effect sizes with CIs; a third case (C3) in a different genre; the evaluation kit is released and extensible |
| "Is it really Straussian GT?" | Table 2 mapping; explicit about what is approximated (no theoretical sampling: a fixed corpus read in shuffled minibatches; selective coding as future work) |

### 10.5 Abstract draft (placeholders in brackets)

> Architectural design decision (ADD) models and design spaces help practitioners reason about
> alternatives. Building them rigorously, typically through Straussian grounded theory over dozens of
> gray-literature sources, takes experts months per domain. We present Delve, a multi-agent workflow that
> operationalizes the Straussian procedure. A Coder agent extracts evidence-backed, paradigm-typed codes; a
> tool-using Taxonomist organizes them into decisions, options, drivers and consequences while a Critic
> judges each draft and decides when the theory is saturated; and an Integrator consolidates and validates
> the model, optionally with human feedback. To evaluate it, we pair [58] recovered sources from [two] published grounded-theory ADD
> studies (ML workflow; RL monitoring) with the experts' models. Delve recovers [X]% of expert decisions and
> [Y]% of options, with [Z]% of cited evidence supporting the extracted options. It outperforms topic
> modeling ([BERTopic]) and a TnT-LLM-style pipeline, and matches a long-context LLM on recall while being
> [more stable and fully traceable]. Ablations show that [open coding with verbatim evidence and the
> critic/judge loops] contribute most. On an engineering narrative without an expert model (Cursor's Git hosting at scale), experts
> judge the mined design space [valid and useful], and it places each organization's system as a distinct
> point. We release Delve, the evaluation kit, and all run artifacts.

### 10.6 Terminology box (for §III)

- "Dimension" = design-space axis (Shaw), **not** a GT "dimension" (the range of a property).
- "Selective coding" in Delve today = use-case **scoping**; core-category integration is future work.
- "Agent" = an LLM-backed role with its own prompt, inputs/outputs and a place in a feedback loop.

---

## 11. Timeline

| Dates | Implementation (§8) | Experiments (§9) | Writing (§10) |
|---|---|---|---|
| **09-26 → 09-29** | B2 fetch sources for C1, C2, C3 (day 1; C1's 2021 links first); P1, P2, P3; B1 GT convert; B7 passage→system mapping for C3 | — | Outline; Table 1 literature pass |
| **09-30 → 10-03** | B8 C4 go/no-go (by 10-01); P4, P5, P7 (drivers) + P17 (relation vocabulary), P9, P11, P12, P13; A1 matcher; A3 harness; L1, L2, L5 | E0 pilots on C3-raw (+ DT dev set if used) | §II related work draft |
| **10-04 → 10-06** | P10, A5 if on schedule; tests; **FREEZE + tag** | E0 calibration (κ, thresholds); budget estimate | §III approach draft, Fig. 2, Table 2 |
| **10-07 → 10-12** | bug fixes only | E1, E2, E3, E8; E5 | §IV benchmark, §V study design |
| **10-13 → 10-16** | A4 analysis, A7 + A9 expert kits | E6 analysis, E7 HITL, E9 C3 analysis, expert ratings (C1/C2 unmatched items + C3) | §VI results; Figs. 1, 3–6; **abstract final 10-16** |
| **10-17 → 10-23** | H2, H3 replication package | re-checks only | Abstract submitted **10-19**; full draft 10-20; internal review 10-21; polish; submit **10-23** |

---

## 12. Open decisions

1. **Personas**: ~~open coding only~~ — **future work, not in the paper (decided 2026-10-02)**; a single coder
   agent is used.
2. **Scope before freeze**: the M items only, or also S (P10, A5)? (P6 and P8 are out of scope.)
3. **Main configuration**: single coder agent (decided 2026-10-02).
4. **Human experts**: 2–3 people × ~2 h (unmatched-item ratings, HITL critique); two authors for κ labeling.
5. **Contacting the GT-study authors** for coding data: useful; consider double-blind and conflict of interest.
6. **Models and budget**: generator family, judge family, embedding model, API budget ceiling.
7. ~~**C1 ground-truth scope**~~ **Decided (2026-10-01):** both studies are compared against two views, the
   paper as reported and the full replication-package model, side by side (§4.1, §5.1 M7).
8. **Dev set**: use the Digital Twins study as a private, unreported development set (proposed, if its
   package is usable), or tune on C3-raw only?
9. **C3 design**: C3-raw as primary with C3-curated as sensitivity (proposed)? Write the optional silver
   decision list?
10. **C3 experts**: who rates C3 (ideally someone with distributed-systems/Git-hosting background)?
11. **Source-text redistribution**: release full texts, or only URLs + fetch scripts (applies to C3's
    Cursor article too)?
12. **C4 (stretch)**: who tries to obtain Lane's thesis (CMU library / KiltHub / DTIC / interlibrary loan) before 10-01?

---

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Long-context baseline matches or beats Delve on F1 | Pre-commit to the secondary claims (grounding, stability, rare-option recall, traceability); honest reporting (§10.3 fallback wording) |
| Sources unrecoverable (C1's 2021 TinyURLs especially) | Check C1 on day 1; archived copies and Wayback; report coverage; optionally restrict the GT to elements whose sources were recovered |
| C1 contaminated (seen in training) | E8 probe; C2 carries the fidelity claim; C1 reported with the caveat |
| C4 sources unobtainable (Lane's thesis, 1980s system papers) | Go/no-go by 10-01; C4 stays future work without affecting the main plan |
| Only two GT studies weakens generality | Per-study reporting with CIs; C3 in another genre; extensible kit; DT as dev set keeps both GT studies clean |
| P7 (drivers) takes longer than 2 days | Ship P7 behind a switch; if late, report drivers from a post-hoc extraction pass and label it as such |
| Pipeline changes eat evaluation time | Hard freeze 10-06; S items dropped first |
| Judge circularity | Cross-family judge (P9) + κ + exact evidence metric |
| "Not agentic enough" | Role framing backed by ablations; HITL |
| API budget overrun | E0 estimate; the cut order in §9.3 |

---

## 14. Key references (to complete)

- M. Shaw, "The Role of Design Spaces," IEEE Software, 2012.
- A. Strauss, J. Corbin, *Basics of Qualitative Research* (1990/1998); J. Corbin, A. Strauss (2008/2015).
- K.-J. Stol, P. Ralph, B. Fitzgerald, "Grounded Theory in Software Engineering Research: A Critical Review
  and Guidelines," ICSE 2016.
- L. K. Nelson, "Computational Grounded Theory: A Methodological Framework," SMR 2020.
- M. Wan et al., "TnT-LLM: Text Mining at Scale with Large Language Models," KDD 2024.
- M. Grootendorst, "BERTopic: Neural topic modeling with a class-based TF-IDF procedure," 2022.
- M. S. Lam et al., "Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM," CHI 2024.
- The four studies in `papers/case-studies/` (ground truth).
- Repo docs: `docs/GT_DESIGN_SPACE_ASSESSMENT.md`, `docs/DESIGN_SPACE_ROADMAP.md`, `docs/VALIDATION_STUDIES.md`.
