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

*Outcome (2026-10-03, B1).*
- The Zenodo record holds the CodeableModels model, so C1 has **two views and a crosswalk**, like C2.
- **Paper view:** Table 2, with 10 decisions, 43 options and 30 forces (151 impacts). It is checked against
  the PDF text.
- **Model view:** 28 decisions and 121 attached options (186 declared), parsed statically.
- **Crosswalk:** 18 decisions are model-only. Details are in `benchmark/c1-ml-workflow/gt/README.md`.

**C2 specifics**: the paper's Table 2 lists 57 options (ADD 2: 16, ADD 6: 9) and 72 drivers (p. 7 says 53 and
59); the model links 62 options (ADD 2: 15, ADD 6: 15), declares a 63rd (Action Failure Rate Monitoring)
without a decision, and has 43 forces. The model view matches the authors' generated views exactly
(`benchmark/c2-rl-monitoring/gt/README.md`). Both views are kept as they are; the differences
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
5. **Candidate-stage recall** (added 2026-10-03): for every gold match, check that the embedding stage put
   the gold partner among the candidates sent to the judge (recall@5 of the candidate list). The judge
   cannot recover a pair the candidate stage never surfaced; low candidate recall is fixed by widening the
   candidate list, not by tuning the judge.
6. **Judge stress test**: ~20 distractor pairs per study that share words but not meaning (e.g. "drift
   detection" vs. "drift compensation") and ~20 paraphrase pairs with little word overlap. The matcher must
   reject the first and accept the second; report both rates. LLM judges are known to be swayed by query-term
   overlap.

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
- **Units of analysis** (added 2026-10-03): GT elements (ADDs, options) are the paired units when comparing
  systems on the same study: for each GT option, recovered or not by each system. Use paired bootstrap CIs
  over GT elements (and McNemar for two systems) in addition to the spread over seeds. With ~60 options per
  study, small differences are not detectable; state the minimum detectable difference instead of implying
  precision.
- **Multiplicity**: the ablation table compares many variants with the full system; control it (Holm or
  Benjamini–Hochberg) and report effect sizes with CIs, never p-values alone.
- **Absolute points**: report differences in absolute F1/recall points (e.g. "+0.08 option recall"), not
  relative gains of means.

### 5.4 Validity safeguards

- **Judge arrangement (decided 2026-10-03).** Only OpenAI models are available in this setup, so the judge is a
  *different OpenAI model* than the generator (test runs: `gpt-5.4-mini` judging `gpt-5.6-luna` output),
  configured as the project's **matching LLM** (`models.matching_llm`). Since 2026-10-03 the project names
  three LLM roles, which should be different models: `generation_llm`, `evaluation_llm` (scoreboard,
  consistency, saturation critic) and `matching_llm`. A model shared between roles runs with a recorded
  warning. Independence is therefore partial: the human gold alignment
  (A6) validates the judge, and the paper states the arrangement as a limitation.
- **Judge from a different model family** than the generator (needs §8 P9; not available in this setup, see
  above). This covers **every** judge: the
  matcher's judge, the human-validation aids, **and the in-loop scoreboard** (until 2026-10-03 `evaluation.judge_model:
  null` fell back to the generator model, so the pipeline graded its own family). Record the judge's model,
  version, prompt and temperature for every judged number.
- **Matcher calibration**: two authors independently label ~100 alignment pairs; report Cohen's κ
  (human–human and human–matcher).
- **Contamination probe**: ask the generator for each ADD model *without sources* and score it with the
  same metrics (§9 E8).
- **Pinned models, seeds and cached outputs**; configs committed; full replication package.
- **Budget-matched comparisons** whenever a variant uses more LLM calls.
- **Freeze the evaluation frame before the first scored run** (added 2026-10-03; done as a written note
  without hashes, `benchmark/README.md` "Evaluation frame", committed at `7c80399` before the first scores): corpus versions (passage
  files + manifest hashes), GT files and views, use cases, matcher thresholds (cross-fitted), judge model
  and prompts, metric definitions and cutoffs, seeds. Anything changed after seeing GT scores is reported
  as such.
- **Measure each stage, not only the end** (A10): where are GT options lost: never open-coded, coded but
  not turned into a value, dropped during the loop (collapse), merged away at consolidation, dropped at
  selection, or present but unmatched? The fix depends on the stage; end-to-end F1 alone hides it.
- **Outputs outside the GT are "unjudged", not false**: the GT reflects one research group's analysis, like
  a shallow pool. Report the share of each system's options that are matched, expert-rated (A7, a sample is
  enough), or unjudged, and give precision both strict (unmatched = wrong) and adjusted (rated valid =
  right). Systems whose outputs differ most from the experts' wording are penalized most by strict precision.
- **Rival hypotheses for every headline gain** (state and check each): more LLM calls (budget), memorized GT
  (contamination probe), matcher leniency toward LLM-phrased items (judge stress test, M10 serialization),
  use-case wording that leaks GT terms (use cases written from the studies' RQs only), and seed luck
  (seed spread).
- **Evidence-link check** (A11): on a sample, verify that linked passages support their value, with a slice
  for `rejected` stances (dense similarity is weak on negation: a passage rejecting X is close to one
  adopting X).

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
| P9 | M | *(2026-10-03: OpenAI-only setup; the evaluation and matching LLMs are separate OpenAI models, `models.evaluation_llm` and `models.matching_llm`, so the wrapper is not needed now)* **Provider-agnostic judge.** A deepeval `DeepEvalBaseLLM` wrapper around `utils.load_chat_model`; `consistency.py` adjudication via `load_chat_model` instead of `AsyncOpenAI` | `evaluation/judge.py`, `evaluation/metrics.py::build_metrics`, `evaluation/consistency.py` | `evaluation.judge_model: anthropic/…` etc. | wrapper contract; fallback | 0.5 d | cross-family judge (validity) |
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
| B6 | M | **C3 corpora**: `benchmark/c3-git-at-scale/` (corpora in `examples/c3-git-at-scale/`) with (a) **C3-raw**: the Cursor article + background sources from `examples/cursor-git-at-scale/references.md` fetched by B2 and segmented by P1; (b) **C3-curated**: the existing `cursor_git_at_scale_documents.json`; (c) a use case (reuse or refine `git_at_scale_config.yaml`) | Keep the curated corpus untouched for comparability with the earlier example runs | 0.25 d |
| B7 | M | **C3 system mapping**: `benchmark/c3-git-at-scale/passage_systems.csv`, where authors map each C3-raw passage to the system(s) it describes (GitHub FS, Google JGit/DHT, GitHub Spokes, Microsoft GVFS/Scalar, Azure DevOps hybrid, Cursor Continuity/Origin, general). Done **before** looking at any Delve output. Plus the optional author-written silver decision list | Needed for the system × dimension matrix (E9) | 0.5 d |
| B8 | C (stretch) | **C4 feasibility check**: obtain Lane's thesis (CMU-CS-90-101); extract the list of surveyed systems and references; try retrieving 5 system descriptions and extrapolate; decide go/no-go by 10-01 (§4.5) | TR-22 and TR-18 already downloaded to the session scratchpad; copy into `papers/base/` if C4 goes ahead | 0.25 d |
| B9 | S | **C3 silver trade-off list** (added 2026-10-04): the authors list the trade-offs the C3 corpus states (its trade-off and decision documents, plus the article). For each trade-off: the systems involved, the quality attributes in tension, and a source reference. Written before any E14 output is seen, and marked as silver (author-written, not expert ground truth) | E14 | 0.25 d |
| B10 | C (stretch) | **C4 benchmark** (only if go): TR-22 Appendix A → `benchmark/lane/gt_model.json` (structural dimensions → decisions/options; functional dimensions → drivers with levels); Appendix B → impacts; fetch/OCR the system sources; passage→system mapping; use case from TR-22 §1 | Same M2 enrichment and freezing rules as C1/C2 | 1.5–2 d |

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
| A10 | M | **Stage-wise recall diagnosis** (added 2026-10-03): for each GT option recovered or missed, trace the pipeline stage where it appears or is lost (open codes → loop iterations → consolidated → selected → matched), from the saved open codes, iterations and match file. Output: a per-study stage funnel | Answers *why* recall is what it is; decides between pipeline fixes (e.g. the value-collapse fix) with evidence; a candidate figure | 0.5 d |
| A11 | S | **Evidence-link check** (added 2026-10-03): sample ~40 value–passage links per study (stratified by stance, oversampling `rejected`), label support by hand; report precision overall and per stance | Validates the deterministic evidence linking that grounding claims rest on | 0.25 d + labeling |
| A12 | S | **Design-point sampler** (added 2026-10-04): `evaluation/design_points.py`. Seeded sampling of k-dimension design points from the selected view, candidate values only, in three groups. **Attested:** all values co-supported by one system, via B7. **Novel:** no single system co-supports them. **Negative controls:** a `rejected` value, or a value from another dimension (revised 2026-10-08: relations are dimension-level, so value-level `constrains` violations cannot be built). Writes `*_design_points.json` and a rating sheet | E13; needs B7 for the attested group | 0.5 d |
| A13 | S | **Design-point judge** (added 2026-10-04). Retrieves each point's evidence passages (`supporting_doc_ids`, open codes). Scores grounding with deepeval Faithfulness (`retrieval_context` = passages) and coherence with a G-Eval rubric, using a judge from another family (cached, like the matcher). Reports scores per group, AUC, and relation validity, and exports a human-rating sheet | E13; reuses `evaluation/judge.py` and the A7 kit | 0.75 d |
| A14 | S | **Value impacts on quality attributes** (added 2026-10-04): for each candidate value, +/−/mixed impacts on a fixed QA vocabulary (ISO 25010 + cost) with rationale and passage ids, plus links from outcome values to candidate values by shared passages. Taken from P7 when built, else post-hoc extraction (labeled). Hand spot-check of about 40 | E14 | 0.5 d |
| A15 | S | **Design-point trade-off analysis** (added 2026-10-04): trade-off profile per design point, cross-dimension tensions, grounding of each tension, agreement with `constrains` relations, recall of the B9 silver trade-offs, and a usefulness rubric (judge + human) | E14; needs A12, A14, B9 | 0.5 d |
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

### 8.6b Next work units (re-prioritized 2026-10-03, following the IR evaluation guidelines)

Principles applied: freeze the evaluation frame before scoring; measure first, then fix, and fix the stage
where recall is lost; keep judges independent of the generator and validated by humans; strong, fair
baselines; paired units and effect sizes; rival hypotheses checked before claims.

| Order | Work unit | Why now | Effort |
|---|---|---|---|
| 1 | *(done 2026-10-03, author checks pending)* **B1** GT conversion (C1, C2; both views; crosswalk; M2 descriptions) + **freeze the evaluation frame** (corpus manifests, use cases agreed by two authors, metric definitions) | Nothing is measurable without it; the frame must be fixed before any score is seen | 1–1.5 d |
| 2 | **P9** provider-agnostic judge, and set a judge from another family for the matcher **and** the in-loop scoreboard | Removes the circularity (the generator grades itself today); needed before any judged number counts | 0.5 d |
| 3 | *(done 2026-10-03)* **A1 (minimal)** matcher: candidate stage + judge, decision alignment, P/R/F1 per view, `match.json` | RQ1/RQ2 numbers; reuse `consistency.py` patterns | 1.5 d |
| 4 | *(scores done 2026-10-03; A10 funnel pending)* **E0 on the existing runs** (C1 `20261002_185546`, C2 `20261002_211657`) + **A10 stage funnel** | First real numbers; shows where options are lost (expected: the value collapse) | 0.75 d |
| 5 | **A6 gold alignment** on E0 outputs (two authors, κ) + **matcher validation** (candidate recall, judge stress test) | Validates the matcher before it scores the main runs | 0.5 d + labeling |
| 6 | **Fix the stage A10 identifies.** If it is the collapse: the tool-based update (`docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md`); re-run E0 and compare the funnel | Evidence-driven fix of the biggest loss | ≈ 2 d |
| 7 | **L1** long-context + **L5** contamination probe (same model as Delve, same corpus, budget recorded) | The baselines reviewers expect first; L5 tests the memorization rival | 0.75 d |
| 8 | **P13** run provenance (config, SHA, models incl. judge, prompts hash, seeds, tokens) | Versioning rule; cheap | 0.25 d |
| 9 | Light **A3/A4** harness and analysis (paired bootstrap over GT elements, effect sizes) | Produces Tables 3–5 | 1 d |
| 10 | **Freeze** (target 10-09), then main runs | | |
| S | **L2** BERTopic, tuned on C3 only (never on GT), + topic metrics (NPMI, diversity) | Strong, non-LLM baseline; topic-modeling reviewers | 1–2 d |
| S | **A7** expert rating of a sample of unmatched items; **A11** evidence-link check | Adjusted precision; grounding validity | 0.5 d + labeling |
| S | Reduced **P12** ablations (no open coding = TnT-style/L3, no judge feedback, no review, rewrite vs. tools) with Holm/BH control | RQ3 | 1 d + runs |

**Scope for the paper (decided 2026-10-04, §12 items 6–10):**
- **RQ1:** decisions and options only. Drivers and relations are reported qualitatively; P4, P7 and P17 →
  future work.
- **Grounding:** P3/A2 are replaced by the evidence-link check (A11) and a sampled grounding check.
- **Baselines:** L1 and L5 only. L2 (BERTopic) and L4 (LLooM) → future work; the "better than topic mining"
  claim is dropped or kept qualitative (§10.3).
- **Ablations (RQ3):** a reduced set: no open coding (TnT-style, L3), no judge feedback, rewrite vs. tools.
  This needs the P12 switches for these three variants only.
- **Seeds:** 3 for main runs, 1–2 for ablations.
- **Judge:** OpenAI only, so no cross-family judge. Reported numbers use a matching LLM other than the
  generator, validated against the human gold alignment (A6); the threat is stated in §5.5.
- **C3:** a reduced, mostly qualitative case. The authors write B7 and B9 before any C3 output is seen. After
  the freeze: C3 runs, the placement matrix (A9) and a small design-point check (E13). E14 is a stretch goal.
- **Future work:** P5, P10, A5, E5, E11, and the wiki/graph export (`docs/DESIGN_SPACE_EXPLORATION.md`).

**Action plan (2026-10-04):**

| When | Implementation and runs | Co-authors (human work, in parallel) |
|---|---|---|
| 10-05 | A10 stage funnel on C2; L5 probe | Ground-truth checks 1–2; use-case agreement (`benchmark/HUMAN_CHECKS.md`) |
| 10-06 → 10-08 | Tool-based update behind a switch (if A10 blames the loop); L1; P13; P12 switches for the reduced ablations; light A3/A4 | A6 gold-alignment labeling; open decisions (check 4); B7 and B9 for C3 |
| 10-09/10 | **Freeze** and tag | — |
| 10-10 → 10-14 | Main runs on C1/C2, 3 seeds: Delve, L1, L5, ablations; C3 runs | Validate the judge against A6 |
| 10-15 → 10-16 | Tables, statistics, C3 placement matrix | Final abstract (10-16) |
| 10-17 → 10-23 | Replication package (H2, H3) | Writing; abstract 10-19, submission 10-23 |

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
- **2026-10-03: B1 and A1 (minimal) done** (`docs/plans/2026-10-03-1804-feat-ground-truth-conversion-and-matcher-plan.md`).
  - **Ground-truth format and validator:** `benchmark/gt_format.py`.
  - **Model views:** a general static CodeableModels parser, `benchmark/parse_code_model.py --study c1|c2`
    (no CodeableModels install, no execution).
  - **Paper views:** C2 from Table 2, Fig. 2 and the catalogue; C1 from Table 2.
  - **Crosswalks:** `benchmark/gt_crosswalk.py`. The author checks of both transcriptions are **pending**
    (study READMEs).
  - **Evaluation frame:** fixed in `benchmark/README.md` before scoring.
  - **Matcher:** `evaluation/gt_match.py`, run with `python main.py --match-gt <taxonomy> --gt
    benchmark/<study>/gt --config <yaml>`.
    - Cosine distance, lower threshold 0 (every `same` comes from the judge) and upper threshold 0.60,
      chosen from ground-truth-only distances: distinct opposite options such as "AutoML"/"No AutoML" sit at
      0.03.
    - A graded deepeval judge, cached.
    - Strict and lenient alignment, placement, per-view metrics.
- **2026-10-03: first ground-truth scores (E0).** These are the selected views of the 2026-10-02 runs,
  judged by `gpt-5.4-mini` with frame settings. The first numbers are not final: the author checks, the
  use-case agreement and the matcher validation (A6) are pending.

  | Run | View | Option P | Option R | Option F1 | Exact R | Related | Decision F1 strict / lenient | Placement |
  |---|---|---|---|---|---|---|---|---|
  | C1 (113 values) | paper | 0.39 | 0.67 | 0.50 | 0.47 | 0.24 | 0.76 / 0.86 | 0.76 |
  | C1 | model | 0.60 | 0.57 | 0.59 | 0.37 | 0.27 | 0.64 / 0.84 | 0.81 |
  | C2 (36 values) | paper | 0.31 | 0.18 | 0.22 | 0.12 | 0.58 | 0.35 / 0.39 | 0.70 |
  | C2 | model | 0.39 | 0.23 | 0.29 | 0.15 | 0.53 | 0.47 / 0.53 | 0.64 |

  Readings and caveats:
  - **C2 recall is low.** Its selected view keeps only 36 candidate values, consistent with the value
    collapse observed in the loop. The stage funnel (A10) is the next measurement.
  - **C2's related rate is high (0.58).** Many values are near misses: the right concern, but not the experts'
    option.
  - **C1 paper-view precision is lower than model view (0.39 vs. 0.60).** 39 C1 values match only
    model-only options, the parts the paper omits. They are left out of the paper-view denominator, as M7
    defines.
  - **Some judge "broader" hits are generous** (e.g. "multiple complementary monitoring metrics" judged
    broader than "Human Review"). A6 must measure this before the numbers count.
  - **OpenAI embeddings are not bit-for-bit deterministic.** One C2 pair crossed the 0.60 boundary on a
    rerun. The judge cache keeps the judge labels reproducible.
  - **Added the same day** (logged in the frame note's "Changes after scores were seen"):
    - **Jaccard** at option level (one-to-one matching of hits; also `same` only) and decision level (strict
      alignment). Judge-mode values:

      | Run | View | Option J | Option J (same only) | Decision J |
      |---|---|---|---|---|
      | C1 | paper | 0.24 | 0.17 | 0.62 |
      | C1 | model | 0.27 | 0.18 | 0.47 |
      | C2 | paper | 0.09 | 0.06 | 0.21 |
      | C2 | model | 0.11 | 0.08 | 0.31 |

    - **An embeddings-only matcher mode** (`--matcher-mode embeddings`). With its ground-truth-derived
      threshold (0.18) it finds **no match** in either run. System-vs-expert distances start at 0.21, and the
      judge's `same`, `related` and `different` pairs overlap almost fully in distance (C1 medians 0.44,
      0.49, 0.52). This is evidence for the rival-hypothesis section: distance alone cannot do the matching,
      so the judge is needed. Its leniency still has to be validated (A6).
  - **2026-10-04 — rescored with the configured matching LLM `gpt-5.6-luna`** (also the generator, so not
    independent; outputs in `examples/<case>/gt_luna/`; frame-note change log).

    | Run | View | Option P / R / F1 | Jaccard | Exact R | Related | Decision F1 strict / lenient | Placement |
    |---|---|---|---|---|---|---|---|
    | C1 | paper | 0.52 / 0.65 / 0.58 | 0.26 | 0.14 | 0.26 | 0.67 / 0.84 | 0.77 |
    | C1 | model | 0.65 / 0.55 / 0.60 | 0.29 | 0.17 | 0.33 | 0.68 / 0.83 | 0.88 |
    | C2 | paper | 0.45 / 0.40 / 0.43 | 0.13 | 0.05 | 0.53 | 0.35 / 0.39 | 0.60 |
    | C2 | model | 0.50 / 0.40 / 0.45 | 0.15 | 0.05 | 0.44 | 0.47 / 0.53 | 0.67 |

    **Qualitative findings.**
    - **C1:**
      - 9 of the paper's 10 decisions are found (lenient). Strong: data ingestion 4/4, feature persistence
        2/2, batch vs. real time 2/2. Weak: "when and how to train" 0/3, model building 1/3, AutoML 1/2,
        triggers 3/6.
      - 29 values match model-only options, in parts the paper omits: integration 6/7, serving 4/5,
        CI/CD 4/4, testing 6/14. Most "extra" values are expert content beyond the paper.
      - Matches are mostly `broader` / `narrower` (granularity mismatch), not `same`.
      - 3 dimensions have no expert counterpart (model registry, federated learning, governance), which is
        a case for the A7 rating.
    - **C2:**
      - The selected view keeps only 36 candidate values in 10 dimensions.
      - Coverage is skewed. Good: monitoring signals 11/16, degradation tests 4/6, hacking detection 5/9.
        Missed: safe exploration 0/3, false-alarm control 0/4. Nearly missed: automated response 1/9,
        hacking mitigation 2/10.
      - About half the values are `related` near misses.
      - One dimension is misplaced ("Reward-Hacking Detection Methods" aligns with the experts'
        monitoring-signal decision), so placement is 0.60.
      - 5 of 10 dimensions align with no expert decision: audit evidence, runtime safety intervention,
        reward-model training, lineage, policy adaptation.
    - **Reading:**
      - C2's deficit is recall. It matches the **value collapse** observed in the loop: values per
        iteration 282 → 59 at iteration 9 (tool-based update plan §1).
      - Whole decisions with no surviving options (safe exploration, false-alarm control) are what a
        rewrite-style update loses when it compresses the taxonomy.
      - This motivates the **tool-based (operation-based) taxonomy update**
        (`docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md`) as the candidate fix for the
        stage A10 is expected to blame.
      - Next: run the A10 stage funnel on C2 to confirm where options are lost. If the loop is confirmed,
        implement the tool-based update and re-score with the same frame and judge.
    - **Judge sensitivity:** `gpt-5.4-mini` → luna moves C2's option F1 from 0.22 to 0.43 and C1's exact
      recall from 0.47 to 0.14. A6 must come before any reported number.
  - **Open definitional point:** the "related" rate is implemented as in the frame note (share of *system
    values* whose best label is `related`), whereas M7 above defines it over *GT options*. Decide which to
    report. A change is logged in the frame note's "Changes after scores were seen".
- **2026-10-04: A10 stage funnel on C2 (`benchmark/stage_funnel.py`; run `20261002_211657`; judge
  `gpt-5.6-luna`, also the generator, so diagnostic only).** Outputs in `examples/c2-rl-monitoring/gt_luna/`.

  | Paper view (57 options) | open codes | generate | update 3 | update 7 (peak) | update 8 | review | consolidated | selected |
  |---|---|---|---|---|---|---|---|---|
  | Options present | 56 | 29 | 17 | 44 | 30 | 30 | 28 | 23 |

  - **The rival "never open-coded" is rejected:** 56 of 57 options (model view: 60 of 62) are in the open codes.
  - **The loop loses them:** presence follows the value count (iteration 3: 213 → 46 values; iteration 8:
    282 → 59). The update after the peak loses 15 options for good (one more is unresolved: only unjudged stages follow its last presence). 46 options drop out at some update and come
    back later, so the space is rebuilt and lost again rather than accumulated.
  - **After the loop:** consolidation loses 5 more, selection 6.
  - **The funnel's candidate gate reproduces the official match** at the selected stage (23 both, 0 disagreements).
    The open-codes gate still needs the hand check (`*_stage_funnel_handcheck.csv`, about 20 options).
  - **Consequence:** the tool-based update (`taxonomy.edit_mode: tools`) targets the stage that loses most options.
    It is compared with `rewrite` and with `rewrite_restore` (rewrite plus restoring dropped evidence-backed
    values), 3 seeds each, with the same frame and judge (plan
    `docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md`, U7).
- **2026-10-05: U7 edit-mode comparison on C2** (one run per mode, same config and code, `edit_max_steps`
  12; judge `gpt-5.6-luna`, also the generator; outputs in `examples/c2-rl-monitoring/u7/`). Paper view
  (model view within ±0.03 except where noted):

  | Mode | Option P / R / F1 | Option J | Exact R | Decision F1 strict / lenient | Selected (dims / values) | Tokens | Scoreboard |
  |---|---|---|---|---|---|---|---|
  | rewrite | 0.28 / 0.23 (13/57) / 0.25 | 0.13 | 0.04 | 0.53 / 0.65 | 8 / 70 | 4.5M | 0.60 |
  | rewrite_restore | 0.37 / **0.93** (53/57) / **0.53** | 0.14 | **0.44** | 0.52 / **0.75** | 20 / **381** | **13.7M** | 0.49 |
  | tools | 0.34 / 0.58 (33/57) / 0.43 | **0.21** | 0.19 | 0.30 / 0.47 | 20 / 182 | 8.6M | 0.61 |

  - **Values per iteration:** rewrite collapses again (241 → 80 at update 8); rewrite_restore only grows
    (→ 525; 2,116 restorations over the run: each rewrite keeps dropping evidence-backed values); tools grows
    steadily (→ 269).
  - **Funnel (paper view, present at review → selected):** rewrite 16 → 13 (22 options lost for good at
    update 8); rewrite_restore 53 → 50; tools 44 → 32 (selection is now its largest loss: 10 options).
  - **Reading:** keeping evidence-backed values explains most of the recall gain (the confound flagged in the
    plan review): rewrite_restore recovers almost every option, but by volume (381 values for 57 options,
    lowest one-to-one Jaccard, lowest scoreboard, 3× the tokens of rewrite). Tools gives a more compact space
    (best Jaccard and scoreboard) at half rewrite_restore's tokens, but loses options at selection and
    fragments decisions (20 dimensions for 7 decisions; strict decision F1 0.30).
  - **Caveats:** a single run per mode (the rewrite collapse is stochastic; the 2026-10-02 rewrite run had
    recall 0.40); a non-independent judge; lenient hits (`broader`/`narrower`) favor large spaces, so
    precision does not penalize redundancy, while Jaccard does.
  - **Open questions for the paper:** whether to report option F1 alone or with Jaccard/size; whether
    selection should be tuned for tools mode (min-support, dimension merging); repeated runs (KTD13) before
    any claim.
- **2026-10-05: round 2 on C2: tools + decision-point granularity rule, and the relevance-filter switch**
  (one run, 10.5M tokens; filter-off view rebuilt without an LLM). Paper view: option P/R/F1/J 0.41 / 0.79 /
  0.54 / 0.25 with the filter, 0.41 / 0.91 / 0.56 / 0.25 without it; strict decision F1 0.45 / 0.46
  (round 1 tools: 0.30); 19 dimensions instead of 30; every update ended with finish; scoreboard 0.70. The
  relevance filter still drops 7 options with no precision gain. Details:
  `docs/paper/results/2026-10-05-c2-update-strategy-comparison.md` (section 3b).
- **2026-10-05: C1 check of tools + M2** (one run, 17.5M tokens, 44 min). The relevance filter kept all 30
  dimensions (no effect on C1). Paper / model view: option P 0.38 / 0.58, R 0.79 / 0.75, F1 0.51 / 0.66,
  J 0.19 / 0.30; strict decision F1 0.62 / 0.79. Against the 2026-10-02 rewrite run (older prompts, not
  like-for-like): higher recall in both views, better model-view scores, lower paper-view precision and F1.
  No collapse (76 → 344 values). Section 3c of the results file.

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
  7. **Design-space fitness** (added 2026-10-04):
     - **Reconstruction:** each system as a design point. Analysis 2 reads as "can the space express every
       system's architecture".
     - **Leave-one-system-out:** rebuild the space without one system's passages (e.g. Cursor's), then
       check whether that system can still be expressed. This tests generalization.
     - **Sampled design points:** E13.
     - **Trade-offs of design points:** E14.
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

**E12 — Pending: wording sensitivity of the ground-truth views (RQ1 robustness; added 2026-10-04)**
- **Question:** do the RQ1 conclusions depend on how richly the experts described their options?
- **Headline setting:** an option shared by the paper and model views is matched, in both views, with the
  paper view's text (`gt_match.VIEW_TEXT_PRECEDENCE`).
  - For C2, that is the catalogue memo's description; the model's own link descriptions are shorter.
  - So the paper-vs-model comparison isolates scope from wording.
- **Rival hypothesis:** richer expert text makes matches easier and inflates absolute scores (both views
  alike).
- **Sensitivity run:**
  - Score the model view on the model's own wording: precedence `("model", "paper")`, or the model view
    alone.
  - Same runs, same matching LLM, same thresholds.
  - Report option and decision P/R/F1/Jaccard next to the headline numbers.
- **Reading:**
  - Conclusions that hold under both wordings are robust to description richness.
  - Large drops point to a wording effect, to be reported as a limitation.
- **Scope and cost:**
  - Only C2 is affected (C1's views share text).
  - Cost: new judge calls on the borderline C2 pairs, cached.
- **To build if scheduled:** a `matcher.text_precedence` setting (or a `--gt-view model` restriction) passed
  to `ground_truth_options`; log the run as a sensitivity analysis, not a frame change.

**E13 — Proposed: design-point validation on C3 (RQ6; added 2026-10-04)**
- **Question:** can architects compose workable designs from the space?
  - A *design point* takes one candidate value from each of k ≥ 2 dimensions of the selected view.
  - Fitness for use means the space generates grounded, coherent design points and rejects incoherent ones.
    Per-value grounding alone is true by construction, because every value carries evidence links.
- **Sampling** (A12, seeded):
  - k = 2–3 dimensions per point.
  - About 30 points per group, from one to two C3 runs.
- **Three groups:**
  - **attested:** one system supports all chosen values (needs B7's system mapping);
  - **novel:** no single system co-supports the values. Exploring these combinations is an intended
    contribution: an ungrounded point can be novel and valid, and only some will be unfeasible;
  - **negative controls:** should fail. A `rejected` value in one slot, or a slot filled with a value taken
    from another dimension. Relations are recorded between dimensions, not values, so a value-level
    `constrains` violation cannot be built; the relations among a point's dimensions are recorded instead.
- **Framing (revised 2026-10-08):**
  - The judged points measure the **coherence of the design space**: can it be traversed into workable
    designs, and which dimension pairs produce incoherent combinations? A pair that does may really be one
    decision.
  - Grounding is reported per group, but it is not a pass/fail criterion for novel points: a novel point
    is unstated by definition.
  - Novel points get a three-way verdict: workable, workable with stated conditions, or unfeasible, each
    with a reason. The line between novel-but-valid and unfeasible is a judgment call, so it is reported as
    a distribution with examples, and checked by the human raters.
  - **Usability** is claimed only from the human task below, not from the judged sample.
  - **Judge family:** only OpenAI models are available, so the judge is a different OpenAI model from the
    generator, validated by the human check. This is stated as a limitation.
- **Scores** (A13), with a judge from a different model family than the generator:
  - **Grounding:** deepeval Faithfulness against the passages retrieved for the point's values. Does the
    evidence support each choice, and does nothing contradict combining them?
  - **Coherence:** a G-Eval rubric. Would an architect accept this combination as a workable design?
- **Report:**
  - scores per group;
  - **discrimination**, as the AUC of attested vs. controls and novel vs. controls. A check that cannot
    reject the controls is uninformative.
  - **relation validity:** do the taxonomy's own `constrains` relations predict the combinations the judge
    calls incoherent?
- **Human check:**
  - Two raters score about 30 points on the same rubric (extending the A7 rating kit). Report κ
    human–human and human–judge.
  - A short fit-for-use questionnaire, answered by a few architects or developers: are the dimensions
    understandable and distinct, and would you use them?
  - **Usability task (added 2026-10-08):** 2–3 raters get a scenario from the article (e.g. "host millions
    of short-lived agent repositories without losing strong consistency"). They pick a design point from
    the taxonomy, then rate whether the space helped and what was missing.
- **Rival hypotheses:**
  - **Judge circularity:** use a different-family judge, validated by the human check.
  - **Novel points rated low only because they are unattested:** the attested group separates these.
- **Cost:** no new pipeline runs; about 200–300 judge calls per run (cached).

**E14 — Proposed: trade-off assessment of design points on C3 (RQ6; added 2026-10-04)**
- **Question:** does the space make the **trade-offs** of a design explicit? When a design point picks
  values across dimensions, which quality attributes improve, which degrade, and are those tensions
  grounded in the corpus?
- **Inputs:**
  - **QA impacts per candidate value** (A14). Each value gets +, − or mixed impacts on a fixed
    quality-attribute vocabulary (ISO 25010 sub-characteristics plus cost), each with a rationale and its
    evidence passages.
    - Taken from P7's value impacts when P7 is built; otherwise extracted post hoc from each value's
      evidence passages and open codes, and labeled as post hoc.
    - Outcome values are linked to the candidate values whose passages they share.
  - **A silver trade-off list for C3** (B9): written by the authors from the corpus's trade-off and decision
    documents and the article, before seeing outputs.
- **Analysis** (A15):
  1. **Trade-off profile per design point:** aggregate its values' impacts. Flag *cross-dimension
     tensions*: two chosen values pushing one quality attribute in opposite directions, or one value's gain
     paid by another's loss.
  2. **Grounding of each tension:** do the passages of both values support it?
  3. **Agreement with the taxonomy's relations:** are tensions concentrated on dimension pairs linked by
     `constrains` relations?
  4. **Recall of the silver trade-offs:** which known trade-offs appear as tensions for the attested design
     points (Spokes, Continuity/Origin, GVFS/Scalar)?
  5. **Usefulness:** the judge and the human raters score the trade-off explanation of each sampled point
     (is it correct, complete, and actionable for an architect?).
- **Rival hypotheses:**
  - **Impact extraction and judging done by the same model family:** keep them separate, and spot-check
    impacts by hand (about 40, as in A11).
  - **Generic quality-attribute talk** ("improves scalability" everywhere): require passage-level support
    per impact, and report how specific the impacts are (the share of values whose impacts differ from
    their dimension's other values).
- **Cost:** no new pipeline runs. One extraction call per value (about 20–40 on C3, cached) and one judge
  call per design point.
- **Applicability:** C1/C2 have expert forces and impacts (C2's model view has 150 option–force impacts), so
  the same profile can later be validated against ground truth there. C3 is the qualitative running example.

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
| E12 (pending) | 0 new pipeline runs (rescoring of existing C2 runs with the model's wording) |
| E13 (proposed) | 0 new pipeline runs (uses E9's C3 runs; ~200–300 judge calls per run) |
| E14 (proposed) | 0 new pipeline runs (~20–40 impact extractions + 1 judge call per design point) |
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
| ~~Better than topic mining~~ (dropped 2026-10-04 with L2; at most a qualitative contrast in Fig. 1) | — | — |
| The update strategy explains recall (added 2026-10-04) | A10 stage funnel; rewrite vs. tools ablation | if the tool-based update does not fix the collapse: "rewrite-style updates compress the design space; the funnel locates the loss" (a diagnostic finding) |
| Competitive with or better than long-context LLMs | E2 vs. L1, E6 stability | "comparable recall, with higher traceability and stability" |
| The GT-specific agentic components matter | E3 TnT-style vs. Straussian; the largest ablation deltas | name the components that matter, report the null ones |
| Delve works without ground truth, in another genre | E9 expert ratings, placement matrix | "plausible and traceable; experts flagged X" |
| The results are not memorization | E8 | "the RL study (post-cutoff) confirms…" |

### 10.4 Anticipated reviewer objections and prepared answers

| Objection | Answer (and where it is in the paper) |
|---|---|
| "This is a pipeline, not an agent." | Roles with feedback loops and autonomous stopping; ablations show each loop's contribution (Table 5). The track also lists multi-agent workflows |
| "Why not just prompt a long-context model?" | L1 baseline; grounding and stability results; cost at scale; traceability for human-led GT |
| "LLM judge evaluating LLM output." | A matching LLM other than the generator (OpenAI only, so not cross-family; stated as a threat), κ against human gold labels (A6), judge-sensitivity report, exact hallucinated-evidence metric, expert ratings |
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

> **Revised 2026-10-04 (current):** the action plan in §8.6b, under "Action plan (2026-10-04)". Freeze
> 10-09/10; main runs 10-10 → 10-14; analysis 10-15 → 10-16; writing from 10-17.
>
> **Revised 2026-10-03** (superseded; the original table below is kept for reference): 10-03 → 10-05 B1 + frame freeze,
> P9, A1 minimal; 10-06 → 10-08 E0 + A10 funnel, A6 gold + κ, fix the lossy stage (tool-based update), L1/L5,
> P13, harness; **FREEZE 10-09**; 10-09 → 10-13 main runs (3 seeds) + L2/ablations if on time; 10-14 → 10-16
> analysis and results, abstract final; 10-17 → 10-23 writing, replication package, submit. Order of work:
> §8.6b.

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
6. **RQ1 scope** — **decided 2026-10-04:** decisions and options only; drivers/forces and relations reported
   qualitatively (P4, P7, P17 → future work).
7. **Collapse fix** — **decided 2026-10-04:** the tool-based update, behind a switch, if the A10 stage funnel
   blames the update loop; it doubles as the "rewrite vs. tools" ablation.
8. **Baselines** — **decided 2026-10-04:** L1 + L5 only; L2 BERTopic → future work.
9. **C3** — **decided 2026-10-04:** reduced, mostly qualitative case: B7, B9, the placement matrix (A9) and a
   small E13; E14 as a stretch goal.
10. **Seeds** — **decided 2026-10-04:** 3 for main runs, 1–2 for ablations. Judge: OpenAI only (no
    cross-family judge); the matching LLM for reported numbers differs from the generator and is validated
    against A6.
11. **Main update strategy** — **decided 2026-10-05:** `taxonomy.edit_mode: tools` is the main configuration
    (lower cost than `rewrite_restore`, no collapse, best one-to-one option fit, every change logged; it is
    the paper's tool-using Taxonomist). `rewrite` and `rewrite_restore` are ablations: `rewrite_restore`
    measures how much recall comes from never losing evidence-backed values. Evidence:
    `docs/paper/results/2026-10-05-c2-update-strategy-comparison.md`. Open: tools mode fragments decisions
    (20 dimensions for 7) and loses options at selection; addressed 2026-10-05 without tuning to the scores: `taxonomy.relevance_selection` switch (off = no LLM relevance filter) and a decision-point granularity rule plus a one-time structural check in tools mode (logged in the frame's change log). To check on C1 and in the repeated runs.
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
