# Delve: An Agentic Workflow for Mining Architectural Design Spaces from Practitioner Literature

**Working manuscript — 9 October 2026. Anonymous draft.**

This draft describes the implementation on `main` after PR #9 (commit `e86c319`); this file is edited on branch
`feat/paper-and-experiments`. The study design is prospective: the freeze and the main runs have not taken place.
Bracketed `TODO` markers identify missing measurements, references, or decisions. Section 9 contains author-facing
notes and must be removed before submission. The prose is intended for a 10-page IEEE conference paper; page fit
has not been checked in IEEEtran.

## Abstract

Architectural design spaces organize the decisions engineers face and the alternatives available for each decision. Practitioner literature provides evidence for these alternatives, but extracting a coherent model requires repeated interpretation, comparison, and revision. We present Delve, an orchestrated agentic workflow that applies open coding and iterative category development to mine architectural design spaces from a fixed corpus. A Coder extracts passage-level concepts, a Taxonomist organizes them into decision points and candidate decisions through validated editing operations, and a Critic provides quality feedback and assesses conceptual coverage. A final integration stage consolidates and scopes the model. The workflow retains intermediate artifacts, logs every model edit, and links candidate decisions to source passages for inspection. We specify an evaluation against two published architectural decision studies, using both their reported paper models and their full replication models. The evaluation compares expert-model agreement, stability, and cost with a same-model long-context baseline and a corpus-free probe of prior model knowledge, and isolates the contribution of open coding, critic feedback, and the editing mechanism. [TODO: replace this prospective sentence with the completed evaluation and its principal numerical findings.] Delve investigates whether explicit coding artifacts and feedback improve architectural knowledge extraction beyond direct model generation, while preserving the distinction between automated model construction and researcher-led grounded theory.

**Keywords:** agentic AI for software engineering; architectural design decisions; design spaces; grounded theory; gray literature.

## 1. Introduction

Software architecture involves choosing among alternatives under competing requirements. A practitioner seeking to design monitoring infrastructure, for example, needs to identify both the relevant decisions and the options available for each decision. A list of recurring topics offers limited guidance: it may identify monitoring or reward hacking without distinguishing what an engineer can choose. A design space makes this distinction explicit by organizing decision points and their alternatives. It can support systematic comparison of designs and expose choices that an engineer might otherwise overlook [1].

Much of the practical knowledge needed to construct such spaces appears in gray literature: engineering articles, technical blogs, discussions, and practitioner reports. Published studies have used Straussian grounded theory to interpret these materials and build architectural design decision models, including models for machine-learning workflows and monitoring deployed reinforcement-learning systems [2, 3]. Their models provide a useful reference for studying automated extraction because the intended output extends beyond document topics to decisions, alternatives, and relationships.

Large language models can generate taxonomies and induce concepts from unstructured text [4, 5]. However, producing a plausible taxonomy does not establish that it captures architectural alternatives at an appropriate granularity. Incremental generation also introduces a state-management problem: as the model grows, each revision must preserve earlier alternatives while integrating new evidence. A revision that re-emits the whole model can silently drop alternatives that earlier evidence supported. These considerations motivate an evaluation of the workflow surrounding the model, rather than an evaluation based solely on the fluency of its final output.

We present **Delve**, an orchestrated agentic workflow for mining architectural design spaces. Its roles communicate through a shared model and explicit feedback. A Coder extracts concepts from individual passages. A Taxonomist builds the initial model and then revises it through a fixed set of validated editing operations, each of which is checked and logged. A Critic evaluates drafts and identifies concepts not covered by the preceding model. Consolidation and scoping produce the final model. Human feedback can seed a subsequent run. The workflow is bounded: the corpus and orchestration are specified in advance, and the Taxonomist's tools edit the shared model only; no role collects new sources.

Our central question is whether this explicit decomposition improves the recovery of architectural knowledge. We assess agreement with published expert models, sensitivity to run variation, and resource consumption. Expert-model agreement is treated as a reference measure rather than proof that the expert model exhausts all valid interpretations. A third case, concerning Git hosting at scale, explores how the extracted space can represent concrete systems without a published expert model.

The intended contributions are:

1. An implemented workflow for architectural design-space extraction, with passage-level codes, iterative feedback, validated and logged model edits, conceptual-coverage stopping, consolidation, and inspectable intermediate artifacts.
2. An evaluation kit linking published source inventories to two views of each expert decision model (paper and replication package, with a crosswalk), and a matcher that aligns extracted alternatives and decision points with them.
3. An empirical assessment of fidelity, component effects, stability, and cost. [TODO: substitute completed findings; this contribution is currently pending.]

The scope is architectural knowledge extraction for software understanding and design comparison. We do not evaluate whether the extracted models improve actual architecture decisions or reduce the total duration of a human research study.

## 2. Background and Related Work

### 2.1 Design spaces and architectural decision models

Shaw describes design spaces in terms of decisions, their alternatives, and complete designs represented as points in the space [1]. Dependencies between decisions can constrain which combinations make sense. We use **decision point** for a question requiring a choice and **candidate decision** for an alternative answer. A **driver** is a requirement, constraint, risk, or quality consideration influencing that choice. A **relation** connects decision points. This vocabulary separates design choices from themes and from their consequences.

Warnett and Zdun investigate architectural decisions in machine-learning workflows through practitioner literature and report a subset of their model [2]. Fang, Warnett, and Zdun study decisions for monitoring deployed reinforcement-learning systems [3]. We use the studies as expert references for reconstruction from their source inventories. Because the published articles and replication models may differ in scope, both representations are retained rather than silently selecting one as the definitive reference.

### 2.2 Grounded theory as a methodological reference

Grounded theory involves systematic development of concepts and their relationships through engagement with data. The distinction between using selected techniques and conducting a grounded-theory study matters: Stol et al. identify methodological problems when studies combine practices without explaining their methodological commitments [6]. Delve uses open coding, iterative category development, comparison with new data, and recorded revision explanations as computational instruments inspired by Straussian grounded theory.

The current implementation does not perform theoretical sampling. It reads a fixed corpus in shuffled minibatches. Its final selection stage scopes categories by minimum evidence rather than integrating them around a core category. Its stopping signal assesses conceptual coverage, not theoretical saturation in the full methodological sense. These boundaries qualify the use of grounded-theory terminology throughout the paper.

### 2.3 LLM-based text mining

TnT-LLM generates and refines a label taxonomy and then uses model-generated labels to support classification [4]. LLooM induces higher-level concepts and supports mixed-initiative analysis [5]. BERTopic provides an embedding-based topic-modeling reference using class-based TF-IDF [7]. These approaches establish relevant alternatives for organizing unstructured text. Delve targets a more specific output structure: decision points whose candidate decisions answer the same choice, with links to practitioner evidence and dependencies between decisions.

Our experimental comparison focuses on direct generation by the same model, which is the alternative a practitioner is most likely to try. Topic-modeling and taxonomy-generation workflows remain relevant related work; adapting them to produce decision points and alternatives would add an interpretation layer of its own, and we leave that comparison to future work.

### 2.4 Agentic software analysis

Delve operates as a stateful workflow in which model-backed roles perform bounded tasks and influence later steps through artifacts and feedback. The role decomposition is an architectural description, not a claim that each graph node is an independent autonomous agent. The Taxonomist is the most agentic role: during revisions it chooses which editing operations to apply, receives the result of each one, and decides when it has finished, within a bounded number of turns. [TODO: add closely related architectural-knowledge extraction and agentic software-analysis work following a focused literature review.]

## 3. Delve

### 3.1 Shared representation and orchestration

Delve represents a design space as decision points containing candidate decisions and dimension-level relations. In the implementation these are `Cluster`, `Value`, and `Relation`. Candidate decisions store descriptions and supporting document identifiers. A status records whether sources adopt a choice (accepted), reject it (rejected), disagree about it (mixed), or report an outcome. Outcomes are kept separate from options in the evaluation because an effect of a choice is not itself necessarily an alternative.

The graph implements corpus loading, optional summarization, minibatch construction, open coding, taxonomy generation or update, evaluation, saturation checking, review, dimension merging, value consolidation, evidence linking, selection, and document labeling. The shared state retains codes, model revisions, explanations, the operation log, and feedback. In training mode, the update loop ends when the stopping conditions hold or the corpus is exhausted. A saved model and external feedback can initialize a subsequent run.

| Role | Responsibility | Current mechanism |
|---|---|---|
| Coder | Extract passage-level concepts and their source stance | Structured LLM output per passage |
| Taxonomist | Construct and revise decision points, alternatives, and relations; review the final model | Initial generation as structured output; updates and review through validated editing operations (tool calls), each logged |
| Critic | Evaluate drafts and identify previously uncovered concepts | LLM quality scoreboard fed back to the next update; coverage check of each new minibatch (read-only) |
| Integrator | Consolidate and scope the reviewed model | Dimension merging and value consolidation (embedding candidates, LLM adjudication of borderline pairs), evidence linking, minimum-support selection, labeling |

The orchestration fixes the sequence of responsibilities. Roles coordinate through the shared design space and explicit feedback rather than through unrestricted conversation. The generator and critic have separate responsibilities, but that separation alone does not make their judgments statistically or epistemically independent; in the current configuration both use the same model.

**Figure 1 — planned architecture figure.** Show the shared artifacts and the Coder → Taxonomist → Critic loop, including the Taxonomist's tool-editing loop (operations, validation, rejection messages), feedback, the stopping gate, integration, and between-run human feedback. Mark deterministic procedures separately from LLM judgments. Do not show autonomous retrieval.

### 3.2 Passage preparation and open coding

The benchmark corpus builder segments sources into passages of approximately 300 words at paragraph and heading boundaries, preserving code blocks and merging very short passages with neighboring content. Passage identifiers retain their source identity (`sNN_pKK`). The benchmark configurations skip summarization and select raw passage content for open coding. This avoids relying on the default summary-based input when interpreting long practitioner sources.

The Coder processes passages independently with bounded concurrency and produces labels, rationales, document identifiers, and decision statuses. These codes are the intermediate artifacts consumed by taxonomy construction. The current schema does not require a verbatim evidence quote, a passage offset, or a Straussian paradigm kind. Passage-level rationales therefore support inspection but do not establish exact quotation fidelity.

### 3.3 Iterative model construction and criticism

The first minibatch produces an initial taxonomy as structured output. Each later minibatch triggers an update: the Taxonomist receives the current model, the minibatch's passages and codes, and the Critic's feedback, and edits the model through a fixed set of operations. Operations add, move, merge, relabel, or remove candidate decisions; set their status; add evidence; add, rename, split, merge, or remove decision points; and add or remove relations. Every call is validated before it is applied. For example, cited passages must belong to the current minibatch, names must not duplicate existing ones, a split must leave at least two candidate decisions in each part, and the model may not exceed a configured number of decision points. A rejected call changes nothing and returns the reason to the model, which may try again; an update is bounded by a number of turns (12 in the study configurations). The final review uses the same operations, but may reclassify statuses without citing a passage, since its sample is the evidence.

Applied and rejected operations are stored as an operation log with each run, together with the model's explanation. The log makes each revision inspectable and lets a reader trace where a candidate decision came from or why it disappeared. Because operations change only what they name, earlier alternatives are preserved unless an operation removes them. The original mechanism, in which each update re-emits the whole model, is retained as an ablation.

A quality evaluator scores the draft and supplies feedback to later construction steps; in the study configurations it scores every third draft, plus the last draft and the final view, and one criterion (completeness, judged against the use case alone) is reported but not fed back. These intrinsic scores guide the workflow; they are not the outcome measures of the external evaluation. The saturation checker compares the latest minibatch's codes with the taxonomy **before** that minibatch was incorporated. This avoids judging coverage against a revision that has just absorbed the same codes.

The stopping rule combines a consecutive-batch streak with a configurable coverage threshold and a minimum fraction of the corpus processed. The study configurations specify three consecutive covered batches, coverage of 0.9, and a minimum processed fraction of 0.7. These values must be reported with their development history. The signal indicates diminishing conceptual novelty under this procedure; it does not guarantee that all alternatives, dependencies, or counterexamples have been discovered.

### 3.4 Consolidation, provenance, and scoping

After review, Delve merges near-duplicate decision points (embedding distance, with an LLM judge for borderline pairs that merges only when both answer one choice) and consolidates semantically similar candidate decisions in the same way. When sources disagree about a candidate decision, consolidation can merge the stances into a single `mixed` value that keeps both sides as evidence. Evidence linking then associates codes with candidate decisions through semantic similarity and combines the resulting document identifiers with valid identifiers already cited by the model.

This mechanism reconstructs provenance links; it does not prove that a passage supports a candidate decision. Embedding similarity may associate related but substantively different claims. In this paper, linked passages serve as navigational provenance for inspection; we do not measure their evidential support. Candidate decisions with no linked evidence are removed while preserving an inspectable record.

Selection applies two minimum-support rules: a decision point needs evidence from at least two sources and at least two candidate decisions. Decision points that fail either rule are dropped with a recorded rationale. LLM relevance filtering is disabled in the study configurations. The full consolidated taxonomy and the selected subset are both retained. We score the selected view, and a stage funnel reports where expert options are lost across stages, including selection, because scoping may remove valid but sparsely supported expert decisions.

Document labeling assigns a passage to a decision point and, when possible, a candidate decision. The current labeler is single-label. It cannot by itself recover all system–decision placements from a passage that discusses several choices.

**Figure 2 — planned evidence trace.** Select a real passage from the RL-monitoring corpus after outputs are available. Show its code, the operations that placed the resulting candidate decision, its parent decision point, the linked source, and its alignment with the expert reference.

## 4. Evaluation Design

### 4.1 Research questions

We organize the evaluation around three questions:

- **RQ1 — Recovery:** To what extent does Delve recover the expert decision points and their alternatives?
- **RQ2 — Workflow effects:** How does Delve compare with direct long-context generation and with the model's prior knowledge, and which components (open coding, critic feedback, validated editing) contribute to its performance?
- **RQ3 — Reliability and resources:** How sensitive are the outputs to run variation, and what tokens, runtime, and monetary costs does each workflow require?

The Git-hosting case is a supplementary application study. Evidence support, human feedback, driver extraction, impact recovery, and richer structural saturation remain extensions; they are not research questions of this paper.

### 4.2 Cases and corpora

| Case | Expert reference | Sources (usable / listed) | Passages | Words |
|---|---|---:|---:|---:|
| C1: ML workflow | Published paper and replication model [2] | 29 / 29 | 265 | 70,191 |
| C2: deployed RL monitoring | Published paper and replication model [3] | 27 / 29 | 243 | 61,980 |
| C3: Git hosting at scale | None (no published expert model) | 5 / 5 | 48 | 13,817 |

C3 also has a curated variant of 16 documents (5,717 words), used only as a sensitivity check because its headings and organization already encode design interpretations. The source texts are retrieved by scripts and are not redistributed. [TODO: freeze the exact source bytes and corpus hashes used for the evaluation.]

C1 uses archived copies associated with the original study. C2 primarily uses more recent retrieved pages; two of its 29 sources are unavailable, and its manifests describe content drift. We report the missing sources explicitly. Full-reference scores reflect both extraction quality and corpus availability.

### 4.3 Two expert-reference views

Each study has a **paper view**, transcribed from the article, and a **model view**, extracted from the replication package, with a crosswalk that identifies elements occurring in both or in only one view. Descriptions for bare option names are derived from the study evidence. Scope differences are retained rather than reconciled by deleting inconvenient elements.

These references support comparison with a published analysis, not an exhaustive inventory of all valid knowledge. Unmatched system items may be unsupported, outside scope, valid but absent from the reference, or expressed at a different granularity.

### 4.4 Baselines and ablations

- **L1, long-context generation:** the same generator model receives all passages in one prompt and emits the same decision/option representation. We will confirm that each corpus fits within the model's usable input context and report output limits; truncation cannot be introduced silently.
- **L5, prior-knowledge probe:** the same model is asked for the design space with the use case but no corpus. Both expert studies are published, so the model may have seen them; a high score here indicates that part of Delve's agreement may reflect prior knowledge rather than extraction.

Ablations remove one component at a time from the frozen full system: (a) **no open coding**, where the Taxonomist works from the passages directly; (b) **no critic feedback**, where the quality scoreboard is still computed but not passed to the next update; and (c) **whole-model rewriting** instead of validated editing operations. [TODO: (a) and (b) need on/off switches before the freeze; (c) is available.]

### 4.5 Alignment and fidelity metrics

All outputs are normalized to decisions and options. Accepted, rejected, and mixed candidate decisions count as options; outcomes are excluded from matching.

Every system option is compared with every expert option of both views. Each item is serialized with its parent decision and description, embedded, and compared by cosine distance. Pairs farther apart than a fixed upper threshold are labeled different without further judgment. A closer pair is sent to an LLM judge only when one item is among the other's five nearest neighbors. The judge assigns one of five labels: same, broader, narrower, related, or different. It sees the two items in a seeded order, without knowing which comes from the expert model, and compares the options regardless of the decision they sit under. Judge results are cached, so rescoring is deterministic. A system option **matches** an expert option when the label is same, broader, or narrower. Option precision, recall, and F1 are computed per view from these matches. Exact recall, using only the same label, and related pairs are reported alongside.

Decision alignment is derived from the option matches. For each system decision point and expert decision, the share of matched options between the two, over the smaller of their option counts, is computed. **Strict alignment** is a one-to-one assignment over pairs whose share reaches a minimum; **lenient alignment** keeps every such pair, so splits and merges count. Decision precision, recall, and F1 are reported for both. A placement measure checks whether matched options sit under aligned decisions.

The thresholds were fixed on the ground truth before any run was scored. The judge is currently the generator model; its labels will be validated against two authors' independent labels of a sample of pairs, reporting inter-annotator agreement (κ) and judge agreement. [TODO: report the A6 results.]

### 4.6 Stability and cost

We plan three repeated runs per principal configuration (one or two per ablation), with a recorded minibatch shuffle seed. A pipeline seed controls ordering; it does not ensure deterministic provider outputs. Stability will be assessed by comparing the repeated runs' metrics and by pairwise alignment of their outputs within each case. Each run records its tokens and elapsed time; monetary cost will be reported with the pricing date and include generation, feedback, and embeddings. Evaluation (matching) costs will be distinguished from extraction costs.

Results will be reported separately by study and reference view, with descriptive run distributions and uncertainty intervals whose resampling unit is specified. Repeated runs within two domains do not constitute independent domain replications. Inferential claims will therefore remain limited. Failed runs and retry policies will be reported rather than omitted.

### 4.7 Development history and reproducibility

Pilot runs on C1 and C2 informed the development of the workflow, including the choice of validated editing over whole-model rewriting and several thresholds; configuration comments also record calibration on C1 code–option similarities. Neither case can be described as untouched by development. The final study will distinguish development runs from frozen evaluation runs and disclose the settings affected.

Each run will record its configuration, code version, models, a fingerprint of its prompts, its seed, and its token counts. [TODO: the run record is planned before the freeze.] The replication package will include the frozen implementation, normalized reference models, crosswalks, exact configurations, source manifests, prompts, model identifiers, run outputs, alignment decisions, and analysis scripts, as well as a browsable design-space wiki generated from a run. Source redistribution depends on the applicable permissions; URLs and retrieval scripts will accompany content hashes when texts cannot be shared. [TODO: add a working anonymous artifact link after the package is prepared.]

## 5. Results — Pending Evaluation

No outcome claims can be made before the frozen runs. This section specifies the evidence required for the final paper.

### 5.1 RQ1: Expert recovery

[TODO: report per-case, per-view decision P/R/F1 (strict and lenient), option P/R/F1, exact recall, and placement.]

**Table 1 — main reconstruction results.** Rows: case × reference view × system. Columns: decision F1 (strict, lenient), option precision, option recall, option F1, exact recall, and placement. Include the number of decisions/options behind each score.

[TODO: explain representative matched, merged, split, and missed outputs using actual passages. Distinguish absences caused by unavailable sources where possible. Use the stage funnel to show where missed expert options were lost.]

### 5.2 RQ2: Baselines and component effects

[TODO: compare the full workflow with L1 and L5. Report each case separately before drawing cross-case interpretations.]

**Table 2 — ablations.** For each implemented variant, show the change in option F1, decision F1, and extraction tokens relative to the frozen full system. Include run variation and the actual number of successful runs.

[TODO: if the long-context baseline performs equally well or better, state that result directly.]

### 5.3 RQ3: Stability and resources

[TODO: provide per-case variation across seeds, model size distributions, tokens, runtime, and cost. Describe the settings controlling shuffle variation and model sampling.]

**Figure 3 — cost and coverage.** Show option recovery against passages processed, if intermediate outputs can be aligned consistently. Do not interpret conceptual-coverage stopping as full theoretical saturation.

### 5.4 Supplementary Git-hosting case

The C3 corpus is segmented from raw text like C1 and C2. Because three of the described systems appear in only one source, and each source is one organization's write-up, C3 requires evidence from one source instead of two (a decision recorded before any C3 run). A passage-to-system map and a list of trade-offs stated by the sources were drafted from the sources only, before any Delve output was inspected; they await review by two authors.

[TODO: assess whether decision points admit coherent alternatives and whether supported placements distinguish the described systems (system × decision matrix). Unknown placements remain unknown. Report the design-point check: sampled combinations of candidate decisions, grouped as attested by a system, novel, or random control, with a workable / conditional / unfeasible verdict. Account for the single-label passage assignment limitation.]

## 6. Discussion

Delve makes intermediate coding and revision artifacts part of architectural knowledge extraction. Their value must be established by the evaluation: decomposition may improve coverage and inspection, but it also introduces more model calls and additional opportunities for errors. The presence of a Critic does not guarantee better outputs, and passing a conceptual-coverage threshold does not guarantee completeness.

The important methodological distinction is between agreement with a reference model and usefulness for architectural reasoning. A reference may omit valid alternatives, while a generated model may reproduce its names without recovering the supporting argument. Conversely, a system may extract genuine options but group them too broadly, or split one decision too finely, to help an engineer make one choice. Reporting option matching, decision alignment, and placement separately makes these outcomes visible. [TODO: development runs extract more, finer decision points than the expert models; report the frozen runs' counts and discuss granularity.]

Human review remains necessary for checking whether alternatives answer the same decision question, whether evidence supports the claimed scope, and whether relations express a meaningful architectural dependency. Between-run feedback offers a mechanism for correction, but improvement from that interaction remains unmeasured. Similarly, automation cost cannot be equated with saved researcher effort without measuring corpus preparation, validation, and correction time.

[TODO: replace or extend these paragraphs with implications grounded in the completed findings.]

## 7. Threats to Validity

**Construct validity.** Expert models provide reference interpretations rather than exhaustive truth. Paper/model scope differences, uneven option descriptions, and granularity mismatches affect alignment. We retain both views, report exact and broader/narrower matches together with exact recall, and validate the judge against human labels. Evidence links are similarity-based and are not validated in this paper; we use them as navigational provenance only.

**Internal validity.** The development history includes exposure to both evaluated cases. A frozen rerun improves reproducibility but cannot undo this exposure. We will disclose affected settings and avoid held-out claims. The generator, critic, and judge currently use the same model and may share systematic biases; human validation of the judge mitigates this for the outcome measure. Stopping, filtering, and consolidation can alter both recall and precision, motivating component comparisons.

**External validity.** Two studies from one research group provide limited diversity in modeling practices and domains. Hundreds of passages do not substitute for independent studies. The Git-hosting case adds a genre but does not supply comparable ground truth. Results will not establish effectiveness for arbitrary architectural documents, repository artifacts, or industrial design tasks.

**Reliability and conclusion validity.** Live-source drift, unavailable C2 sources, proprietary model changes, nondeterministic inference, and uncertain retrieval reproducibility can affect replication. Exact manifests and run artifacts mitigate but do not eliminate these issues. Three runs per configuration limit statistical power, and repeated seeds measure within-case variation rather than generalization across domains.

**Training-data exposure.** Publication recency alone does not establish absence from training. The corpus-free probe (L5) can reveal some prior knowledge, but failure to reconstruct a model does not prove absence of contamination. We will describe the probe as diagnostic evidence and avoid claims that either case is contamination-free.

## 8. Conclusion

We presented Delve, a stateful agentic workflow for extracting architectural design spaces from practitioner literature. The workflow combines passage-level coding, iterative model revision through validated and logged editing operations, quality feedback, conceptual-coverage stopping, consolidation, and inspectable provenance links. Its methodological scope is an automated aid using grounded-theory techniques over a fixed corpus.

[TODO: insert one sentence stating the principal measured outcome and one sentence identifying the most consequential limitation.]

The evaluation separates expert-model recovery at the level of alternatives and decisions, component effects, and resource use. These distinctions are necessary to assess whether workflow structure contributes useful architectural knowledge beyond what direct generation can provide.

## References — Working List

Full publication metadata must be checked before conversion to BibTeX. The verified sources below support this draft's framing; the related-work search is not yet exhaustive.

1. M. Shaw, “The Role of Design Spaces,” *IEEE Software*, 2012. Author-paper copy: https://cmu-swdesign.github.io/reading/ShawDesignSpace-a.pdf
2. S. J. Warnett and U. Zdun, “Architectural Design Decisions for the Machine Learning Workflow,” *Computer*, vol. 55, no. 3, pp. 40–51, March 2022. DOI: https://doi.org/10.1109/MC.2021.3134800. Verified publication record: https://ucrisportal.univie.ac.at/en/publications/architectural-design-decisions-for-the-machine-learning-workflow/. Replication-package identifier supplied in project notes: https://doi.org/10.5281/zenodo.5730291
3. Z. Fang, S. J. Warnett, and U. Zdun, “Architectural Design Decisions for Monitoring Deployed Reinforcement Learning Systems,” ECSA, 2026. Author-group announcement: https://swa.cs.univie.ac.at/news/story/swa-at-ecsa26. Replication-package identifier supplied in project notes and branch: https://doi.org/10.5281/zenodo.20305497. [TODO: verify proceedings pages and publication DOI.]
4. M. Wan et al., “TnT-LLM: Text Mining at Scale with Large Language Models,” 2024. https://arxiv.org/abs/2403.12173. [TODO: use final KDD metadata.]
5. M. S. Lam, J. Teoh, J. Landay, J. Heer, and M. S. Bernstein, “Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM,” CHI, 2024. https://doi.org/10.1145/3613904.3642830; author preprint: https://arxiv.org/abs/2404.12259
6. K.-J. Stol, P. Ralph, and B. Fitzgerald, “Grounded Theory in Software Engineering Research: A Critical Review and Guidelines,” ICSE, pp. 120–131, 2016. https://doi.org/10.1145/2884781.2884833; author repository: https://cora.ucc.ie/handle/10468/7041
7. M. Grootendorst, “BERTopic: Neural Topic Modeling with a Class-Based TF-IDF Procedure,” 2022. https://arxiv.org/abs/2203.05794
8. [TODO: select and verify the Strauss/Corbin edition that anchors the actual methodological commitments.]
9. [TODO: verify Nelson's computational grounded-theory reference and add recent architectural-knowledge extraction and agentic AI4SE studies.]

---

## 9. Author Notes — Remove Before Submission

### 9.1 What the implementation supports (as of 2026-10-09, `main` at `e86c319`)

| Statement | Evidence | Draft treatment |
|---|---|---|
| Raw passage coding | `nodes/open_coder.py`; study configs set `open_coding.input: content` | Implemented |
| Source segmentation and corpora | `benchmark/build_corpus.py`; C1 265, C2 243, C3 48 passages (texts gitignored) | Implemented |
| Validated editing operations with an operation log | `taxonomy_editor.py`, `tool_update.py`; C1/C2/C3 set `edit_mode: tools` | Implemented; main strategy |
| Whole-model rewriting | `edit_mode: rewrite` (also `rewrite_restore`) | Ablation (c) |
| Dimension cap enforced in tools mode | `TaxonomyEditor(max_dimensions=…)`; study configs set no cap | Implemented; not used by the study |
| Feedback and conceptual-coverage stopping | `graph.py`, `nodes/saturation_checker.py`, settings | Implemented, with limited saturation claims |
| Dimension merging and value consolidation | `nodes/dimension_merger.py`, `nodes/value_consolidator.py` | Implemented |
| Provenance linking | `nodes/evidence_linker.py` | Implemented; links described as navigational, not validated |
| Relevance selection | `relevance_selection: false` in study configs | Off; selection is minimum support only |
| Both reference views and crosswalks | `benchmark/c1-ml-workflow/gt/`, `benchmark/c2-rl-monitoring/gt/` | Implemented |
| Matcher (options, decisions, placement) | `evaluation/gt_match.py`, `main.py --match-gt`, settings in `benchmark/README.md` | Implemented as described in §4.5 |
| Stage funnel | `benchmark/stage_funnel.py` | Implemented |
| Verbatim evidence and paradigm-typed codes | `OpenCode` has doc id, label, rationale, status only | Not claimed |
| Drivers/impacts as output fields | Absent from output schemas | Not claimed |
| L1/L5 baselines | Not implemented | Planned before freeze |
| Ablation switches (no open coding, no feedback) | Not implemented | Planned before freeze |
| Run record (provenance block) | Run metrics (tokens, time) only | Planned before freeze |
| C3 B7/B9 | Agent drafts in `benchmark/c3-git-at-scale/`; author review open | Described as drafts |
| C3 design-point sampler | `benchmark/design_points.py` (attested / novel / control) | Implemented; judge and human rating open |
| Design-space wiki | `benchmark/export_wiki.py` | Artifact only; not a paper contribution |
| C1/C2 untouched | Pilot runs and tuning on both | Held-out wording avoided |
| Researcher time saved | No measurement | No such claim |

### 9.2 Preliminary development observations (not results; pre-freeze, judge = generator)

- **Update strategy, C2** (`docs/paper/results/2026-10-05-c2-update-strategy-comparison.md`, one run each, paper view):
  - Whole-model rewriting lost 22 expert options for good in a single update and ended with option F1 0.25.
  - Validated editing (with the decision-granularity prompt, relevance filter off) reached option recall 0.91 and F1 0.56.
  - This motivated choosing validated editing as the main strategy.
- **C1 check, validated editing** (one run): option F1 0.51 (paper view) / 0.66 (model view); strict decision F1 0.62 / 0.79. Recall is higher than an older rewrite run, but precision in the paper view is lower.
- **Judge sensitivity:** the judge choice moved C2's option score by about 0.2, so the A6 human check comes before any number is reported.
- **Quality probe** (`docs/paper/results/2026-10-08-taxonomy-quality-probe.md`): 20–31% of candidate values answer a different question than their decision point asks; 3–12% are not options at all (goals, principles). Accepted links contain almost no unrelated passages; C2's mixed and outcome links are weaker (small samples).
- **Granularity:** Delve extracts more decision points than the experts (C1 30 vs. 10 paper / 28 model; C2 19 vs. 7; C3 22, no reference). A decision-focus pass is planned but deferred (`docs/plans/2026-10-08-1500-feat-decision-focus-pass-plan.md`); without it, granularity is a discussion point and a threat.

### 9.3 Minimum path to a defensible empirical submission

1. Before the freeze: run record (P13), ablation switches (P12), L1/L5 baselines, and the A6 labeling sheet.
2. Freeze the configuration and source hashes; record the C1/C2-informed tuning history.
3. Main runs, one at a time: C1/C2 × 3 seeds, ablations × 1–2 seeds, baselines, C3.
4. A6 human labels → κ and judge agreement; statistics harness (A3/A4) and tables.
5. Figures and traces from real outputs; replace all prospective phrasing and `TODO` markers.

### 9.4 Suggested 10-page body allocation

| Material | Approximate pages |
|---|---:|
| Abstract and introduction | 1.0 |
| Background and related work | 1.0 |
| Approach and architecture/evidence figures | 2.0 |
| Benchmark and evaluation design | 2.0 |
| Results and main tables | 2.5 |
| Discussion, threats, conclusion | 1.5 |

The official track permits 10 pages plus up to 2 pages for references, requires double-anonymous review, and specifies IEEEtran conference format. Mandatory abstract deadline: **19 October 2026 AoE**. Paper deadline: **23 October 2026 AoE**. Verified 7 October 2026: https://conf.researchr.org/track/saner-2027/saner-2027-agentic-ai4se-track

### 9.5 Claims to settle before submission

- Settled 2026-10-09: the evaluated system uses validated editing operations; whole-model rewriting is an ablation. Describe only that mechanism as the approach.
- Settled 2026-10-09: evidence support is not measured; linked passages are navigational provenance. RQ1 covers decisions and options only.
- Settled 2026-10-09: the matcher scores as implemented (same, broader, and narrower count as matches; exact recall reported alongside).
- Treat intrinsic quality scores as control signals, not independent validation.
- Disclose pilot exposure without implying that a post-pilot freeze restores an untouched evaluation.
- Keep C3-curated sensitivity results separate from raw-text extraction because preorganization can encode the answer.
- Report provider/model settings as actually used (currently `openai/gpt-5.6-luna` for generation, evaluation, and matching; no temperature or effort setting).
- **Anonymity:** the repository name, the GitHub Pages sample wiki (`andresdp.github.io/delve`) and the published C3 sample identify the authors. Use an anonymized artifact for review and do not link these.
- Measure human effort before claiming researcher-time savings; extraction API cost is a different outcome.

### 9.6 Draft provenance

The 7 October version was prepared from an archive of commit `48a2fd1` and planning notes. This revision (9 October) updates it to the implementation on `main` at `e86c319`. Implementation claims were checked against the code and study configurations; corpus sizes were computed from the local corpora; preliminary observations come from the results notes cited in §9.2. No new experiments were run for this revision.
