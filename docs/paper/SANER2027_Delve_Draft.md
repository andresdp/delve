# Delve: An Agentic Workflow for Mining Architectural Design Spaces from Practitioner Literature

**Working manuscript — 7 October 2026. Anonymous draft.**

This draft describes the implementation in the supplied branch archive, whose archive comment identifies commit `48a2fd10ce0398b9ccb07495404d00ac00280920`. The study design is prospective. Bracketed `TODO` markers identify missing measurements, references, or decisions. No comparative evaluation was performed while preparing this manuscript. Section 9 contains author-facing notes and must be removed before submission. The prose is intended for a 10-page IEEE conference paper; page fit has not been checked in IEEEtran.

## Abstract

Architectural design spaces organize the decisions engineers face and the alternatives available for each decision. Practitioner literature provides evidence for these alternatives, but extracting a coherent model requires repeated interpretation, comparison, and revision. We present Delve, an orchestrated agentic workflow that applies open coding and iterative category development to mine architectural design spaces from a fixed corpus. A Coder extracts passage-level concepts, a Taxonomist organizes them into decision points and candidate decisions, and a Critic provides quality feedback and assesses conceptual coverage. A final integration stage reviews, consolidates, and scopes the model. The workflow retains intermediate artifacts and links candidate decisions to source passages for inspection. We specify an evaluation against two published architectural decision studies, using both their reported paper models and their full replication models. The evaluation compares expert-model agreement, evidence support, stability, and cost with a long-context LLM and text-mining baselines, and isolates the contribution of feedback and consolidation. [TODO: replace this prospective sentence with the completed evaluation and its principal numerical findings.] Delve investigates whether explicit coding artifacts and feedback improve architectural knowledge extraction beyond direct model generation, while preserving the distinction between automated model construction and researcher-led grounded theory.

**Keywords:** agentic AI for software engineering; architectural design decisions; design spaces; grounded theory; gray literature.

## 1. Introduction

Software architecture involves choosing among alternatives under competing requirements. A practitioner seeking to design monitoring infrastructure, for example, needs to identify both the relevant decisions and the options available for each decision. A list of recurring topics offers limited guidance: it may identify monitoring or reward hacking without distinguishing what an engineer can choose. A design space makes this distinction explicit by organizing decision points and their alternatives. It can support systematic comparison of designs and expose choices that an engineer might otherwise overlook [1].

Much of the practical knowledge needed to construct such spaces appears in gray literature: engineering articles, technical blogs, discussions, and practitioner reports. Published studies have used Straussian grounded theory to interpret these materials and build architectural design decision models, including models for machine-learning workflows and monitoring deployed reinforcement-learning systems [2, 3]. Their models provide a useful reference for studying automated extraction because the intended output extends beyond document topics to decisions, alternatives, and relationships.

Large language models can generate taxonomies and induce concepts from unstructured text [4, 5]. However, producing a plausible taxonomy does not establish that it captures architectural alternatives at an appropriate granularity or that its supporting passages justify the extracted claims. Incremental generation also introduces a state-management problem: as the model grows, each revision must preserve earlier alternatives while integrating new evidence. These considerations motivate an evaluation of the workflow surrounding the model, rather than an evaluation based solely on the fluency of its final output.

We present **Delve**, an orchestrated agentic workflow for mining architectural design spaces. Its roles communicate through a shared model and explicit feedback. A Coder extracts concepts from individual passages. A Taxonomist builds and revises decision points and candidate decisions. A Critic evaluates drafts and identifies concepts not covered by the preceding model. Review, consolidation, and scoping produce the final model. Human feedback can seed a subsequent run. The workflow is bounded: the corpus and orchestration are specified in advance, and the current Taxonomist produces structured model revisions rather than choosing arbitrary tools or autonomously collecting new sources.

Our central question is whether this explicit decomposition improves the quality and auditability of recovered architectural knowledge. We assess agreement with published expert models, the support supplied by linked passages, sensitivity to run variation, and resource consumption. Expert-model agreement is treated as a reference measure rather than proof that the expert model exhausts all valid interpretations. A third case, concerning Git hosting at scale, is intended to explore how the extracted space can represent concrete systems without a published expert model.

The intended contributions are:

1. An implemented workflow for architectural design-space extraction, with passage-level codes, iterative feedback, conceptual-coverage stopping, consolidation, and inspectable intermediate artifacts.
2. An evaluation kit linking published source inventories to two views of each expert decision model, with an explicit alignment and grounding protocol. [TODO: retain this contribution only after the normalized models and evaluation code are complete.]
3. An empirical assessment of fidelity, component effects, stability, and cost. [TODO: substitute completed findings; this contribution is currently pending.]

The scope is architectural knowledge extraction for software understanding and design comparison. We do not evaluate whether the extracted models improve actual architecture decisions or reduce the total duration of a human research study.

## 2. Background and Related Work

### 2.1 Design spaces and architectural decision models

Shaw describes design spaces in terms of decisions, their alternatives, and complete designs represented as points in the space [1]. Dependencies between decisions can constrain which combinations make sense. We use **decision point** for a question requiring a choice and **candidate decision** for an alternative answer. A **driver** is a requirement, constraint, risk, or quality consideration influencing that choice. A **relation** connects decision points. This vocabulary separates design choices from themes and from their consequences.

Warnett and Zdun investigate architectural decisions in machine-learning workflows through practitioner literature and report a subset of their model [2]. Fang, Warnett, and Zdun study decisions for monitoring deployed reinforcement-learning systems [3]. We use the studies as expert references for reconstruction from their source inventories. Because the published articles and replication models may differ in scope, both representations are retained rather than silently selecting one as the definitive reference.

### 2.2 Grounded theory as a methodological reference

Grounded theory involves systematic development of concepts and their relationships through engagement with data. The distinction between using selected techniques and conducting a grounded-theory study matters: Stol et al. identify methodological problems when studies combine practices without explaining their methodological commitments [6]. Delve uses open coding, iterative category development, comparison with new data, and recorded revision explanations as computational instruments inspired by Straussian grounded theory.

The current implementation does not perform autonomous theoretical sampling. It reads a fixed corpus in shuffled minibatches. Its final selection stage scopes categories to a use case rather than integrating them around a core category. Its stopping signal assesses conceptual coverage, not theoretical saturation in the full methodological sense. These boundaries qualify the use of grounded-theory terminology throughout the paper.

### 2.3 LLM-based text mining

TnT-LLM generates and refines a label taxonomy and then uses model-generated labels to support classification [4]. LLooM induces higher-level concepts and supports mixed-initiative analysis [5]. BERTopic provides an embedding-based topic-modeling reference using class-based TF-IDF [7]. These approaches establish relevant alternatives for organizing unstructured text. Delve targets a more specific output structure: decision points whose candidate decisions answer the same choice, with links to practitioner evidence and dependencies between decisions.

We evaluate the benefit of that specialization rather than assuming that topic mining fails. A reduced Delve configuration inspired by taxonomy-generation workflows must be identified as a **TnT-inspired workflow**, unless it faithfully reproduces the original method. LLooM remains relevant related work even if it is omitted from the experimental comparison.

### 2.4 Agentic software analysis

Delve operates as a stateful workflow in which model-backed roles perform bounded tasks and influence later steps through artifacts and feedback. The role decomposition is an architectural description, not a claim that each graph node is an independent autonomous agent. The current revision mechanism uses structured LLM output; validated tool-based edits are proposed separately and are not part of the evaluated implementation unless completed before the study freeze. [TODO: add closely related architectural-knowledge extraction and agentic software-analysis work following a focused literature review.]

## 3. Delve

### 3.1 Shared representation and orchestration

Delve represents a design space as decision points containing candidate decisions and dimension-level relations. In the implementation these are `Cluster`, `Value`, and `Relation`. Candidate decisions store descriptions and supporting document identifiers. A status records whether a source adopts a choice, rejects it, or reports an outcome. Outcomes are kept separate from options in the evaluation because an effect of a choice is not itself necessarily an alternative.

The graph implements corpus loading, optional summarization, minibatch construction, open coding, taxonomy generation or update, evaluation, saturation checking, review, consolidation, use-case selection, and document labeling. The shared state retains codes, model revisions, explanations, and feedback. In training mode, the update loop ends when the stopping conditions hold or the corpus is exhausted. A saved model and external feedback can initialize a subsequent run.

| Role | Responsibility | Current mechanism |
|---|---|---|
| Coder | Extract passage-level concepts and their source stance | Structured LLM output per passage |
| Taxonomist | Construct and revise decision points, alternatives, and relations | Initial generation and full-model structured revisions |
| Critic | Evaluate drafts and identify previously uncovered concepts | LLM quality judgments and coverage assessment |
| Integrator | Consolidate alternatives and scope the reviewed model | Review, embedding-based merge candidates, adjudication, and selection |

The orchestration fixes the sequence of responsibilities. Roles coordinate through the shared design space and explicit feedback rather than through unrestricted conversation. The generator and critic have separate responsibilities, but that separation alone does not make their judgments statistically or epistemically independent.

**Figure 1 — planned architecture figure.** Show the shared artifacts and the Coder → Taxonomist → Critic loop, including feedback, the stopping gate, integration, and between-run human feedback. Mark deterministic procedures separately from LLM judgments. Do not show an autonomous retrieval or tool-editing loop for the current branch.

### 3.2 Passage preparation and open coding

The benchmark corpus builder segments sources into passages of approximately 300 words at paragraph and heading boundaries, preserving code blocks and merging very short passages with neighboring content. Passage identifiers retain their source identity. The benchmark configurations skip summarization and select raw passage content for open coding. This avoids relying on the default summary-based input when interpreting long practitioner sources.

The Coder processes passages independently with bounded concurrency and produces labels, rationales, document identifiers, and decision statuses. These codes are the intermediate artifacts consumed by taxonomy construction. The current schema does not require a verbatim evidence quote, a passage offset, or a Straussian paradigm kind. Passage-level rationales therefore support inspection but do not establish exact quotation fidelity.

### 3.3 Iterative model construction and criticism

The first minibatch produces an initial taxonomy. Later minibatches trigger model revisions using the current taxonomy, passage information, codes, and feedback. Prompts ask that each decision point represent one choice, so its candidate decisions are alternatives to the same question. Updates can change names, groupings, alternatives, and relations. Their explanations provide a revision narrative, although the current implementation does not record a validated operation log.

A quality evaluator scores the draft and supplies feedback to later construction steps. These intrinsic scores guide the workflow; they are not the primary outcome measures of the external evaluation. The saturation checker compares the latest minibatch's codes with the taxonomy **before** that minibatch was incorporated. This avoids judging coverage against a revision that has just absorbed the same codes.

The stopping rule combines a consecutive-batch streak with a configurable coverage threshold and a minimum fraction of the corpus processed. The supplied benchmark configurations specify three consecutive covered batches, coverage of 0.9, and a minimum processed fraction of 0.7. These values must be reported with their development history. The signal indicates diminishing conceptual novelty under this procedure; it does not guarantee that all alternatives, dependencies, or counterexamples have been discovered.

### 3.4 Consolidation, provenance, and scoping

After review, Delve can merge overlapping decision points and consolidate semantically similar candidate decisions using embedding candidates and LLM adjudication. Evidence linking then associates codes with candidate decisions through semantic similarity and combines the resulting document identifiers with valid identifiers already cited by the model. Source stance can be retained when sources disagree.

This mechanism reconstructs provenance links; it does not prove that a passage supports a candidate decision. Embedding similarity may associate related but substantively different claims. Consequently, evidence support is evaluated separately through inspection of the underlying passages. Unsupported alternatives can be removed while preserving an inspectable record.

Selection filters decision points for relevance and configurable minimum support. The supplied configurations require evidence from at least two sources and at least two candidate decisions. The full consolidated taxonomy and the selected subset are both retained. We use the full consolidated view for the primary reconstruction comparison and report selection effects separately, because scoping may remove valid but sparsely supported expert decisions.

Document labeling assigns a passage to a decision point and, when possible, a candidate decision. The current labeler is single-label. It cannot by itself recover all system–decision placements from a passage that discusses several choices.

**Figure 2 — planned evidence trace.** Select a real passage from the RL-monitoring corpus after outputs are available. Show its code, the resulting candidate decision, its parent decision point, the linked source, and its alignment with the expert reference. Include a questionable link alongside a supported example to expose the limits of reconstructed provenance.

## 4. Evaluation Design

### 4.1 Research questions

We organize the evaluation around three questions:

- **RQ1 — Recovery and grounding:** To what extent does Delve recover expert decision points and alternatives, and how often do its linked passages support the recovered claims?
- **RQ2 — Workflow effects:** How does Delve compare with direct long-context generation and text-mining workflows, and which feedback and consolidation components contribute to its performance?
- **RQ3 — Reliability and resources:** How sensitive are the outputs to run variation, and what tokens, runtime, and monetary costs does each workflow require?

The Git-hosting case is a supplementary application study. Human feedback, driver extraction, impact recovery, and richer structural saturation remain optional extensions; they should become research questions only when supported by completed experiments.

### 4.2 Cases and corpus availability

| Case | Expert reference | Source inventory | Availability reported in the supplied branch |
|---|---|---:|---|
| C1: ML workflow | Published paper and replication model [2] | 29 | 29 usable sources; approximately 70,000 words |
| C2: deployed RL monitoring | Published paper and replication model [3] | 29 | 27 usable sources; approximately 62,000 words |
| C3: Git hosting at scale | No published expert reference | Engineering narrative and background material | Curated examples and illustrative outputs included; raw evaluation corpus pending |

The source counts and word totals above are branch documentation, not an independent verification of the underlying texts. The archive includes source manifests and fetching scripts, but not the ignored raw source texts or generated C1/C2 passage corpora. [TODO: recover and freeze the exact source bytes and corpus hashes used for the evaluation.]

C1 uses archived copies associated with the original study. C2 primarily uses more recent retrieved pages; its manifests describe unavailable sources and content drift. We will report the missing sources and quote-coverage limitations explicitly. Full-reference scores reflect both extraction quality and corpus availability. A restricted analysis may score only expert elements with independently identifiable evidence in the recovered sources, provided that this eligibility rule is established before inspecting system outputs.

### 4.3 Two expert-reference views

Each study will have a **paper view**, transcribed from the article, and a **model view**, extracted from the replication package. A crosswalk will identify elements occurring in both or in only one view. Descriptions for bare option names will be derived from the study evidence and cross-checked before alignment. Scope differences will be retained rather than reconciled by deleting inconvenient elements.

These references support comparison with a published analysis, not an exhaustive inventory of all valid knowledge. Unmatched system items may be unsupported, outside scope, valid but absent from the reference, or expressed at a different granularity. Their assessment is reported separately from reference agreement.

### 4.4 Systems and ablations

The principal baseline receives the same passages in one long-context prompt and emits the same decision/option representation with supporting passage identifiers. It uses the same generator model as Delve. We will confirm that the corpus fits within the model's usable input context and report output limits; truncation cannot be introduced silently.

A BERTopic-based baseline organizes passage embeddings into topics and uses a documented labeling/grouping procedure to produce decision points and alternatives. Because this conversion adds an architectural interpretation layer, its prompts, model calls, and costs are part of the baseline. Unsupported output structures, such as relations, will be reported as not applicable rather than assigned zero performance.

A TnT-inspired workflow removes Delve-specific stages while preserving a comparable taxonomy task. Its deviations from TnT-LLM will be documented. The minimum ablation set removes quality feedback, consolidation, and early stopping individually. An open-coding ablation will be included only after a fair alternative input path is implemented. Variants of features absent from the frozen system will not be described as completed ablations.

### 4.5 Alignment and fidelity metrics

All outputs will be normalized to decisions, options, relations, and provenance. Accepted and rejected candidate decisions count as options; consolidated mixed stances also count as options. Outcomes are excluded from option matching.

Option matching is global across parent decisions so a correct alternative filed under a different decision can still count as recovered. Embedding candidates are checked using graded labels: equivalent, broader, narrower, related, or different. Equivalent matches define exact-option recall. Broader and narrower matches contribute to a separately labeled coverage measure; they do not establish exact reconstruction. Candidate-retrieval recall will be audited because a missed candidate pair cannot be recovered by downstream adjudication.

Decision alignment will combine semantic descriptions with aligned option content. A strict one-to-one assignment supports decision precision, recall, and F1. A separate analysis characterizes merged, split, partial, and missed decisions. Placement-aware option recall assesses whether recovered options appear under aligned decisions. Grouping agreement will be reported only after specifying how multiple alignments are reduced to comparable partitions; otherwise a many-to-many alignment makes a simple adjusted Rand index ambiguous.

The matcher will be validated against independently labeled pairs, including likely matches, near misses, and a sample outside the retrieval candidates. We will report annotator agreement, disagreements, and matcher accuracy. A cross-family model judge is planned, but human validation remains necessary. Calibration data and test alignment data will be separated, and every threshold will be recorded.

### 4.6 Grounding, stability, and cost

Grounding comprises two measures. **Identifier validity** checks whether a cited passage exists in the run corpus. **Evidence support** checks whether the cited text justifies the option description, including its claimed scope and stance. Blind human assessment of sampled links is the preferred reference; automated judgments may supplement it after validation. The current schema cannot support an exact-quotation hallucination metric because it does not store mandatory quotes. Evidence coverage also records the share of extracted options with at least one supported passage.

We plan five repeated runs per principal configuration, with a recorded minibatch shuffle seed and model settings. A pipeline seed controls ordering; it does not ensure deterministic provider outputs. Stability will be assessed by pairwise semantic alignment of outputs within each case. Tokens, elapsed time, and monetary cost will be reported with the pricing date and include generation, feedback, embeddings, and baseline labeling. Evaluation costs will be distinguished from extraction costs.

Results will be reported separately by study and reference view, with descriptive run distributions and uncertainty intervals whose resampling unit is specified. Repeated runs within two domains do not constitute independent domain replications. Inferential claims will therefore remain limited, and a five-pair comparison will not be presented as strong evidence of general superiority. Failed runs and retry policies will be reported rather than omitted.

### 4.7 Development history and reproducibility

The supplied progress log describes C1/C2 pilot runs and threshold adjustments informed by their outputs. Configuration comments also identify calibration using C1 code–option similarities. Neither case can currently be described as untouched by development. The final study will distinguish development runs from frozen evaluation runs and disclose the settings affected. If an additional untouched case is unavailable, this limitation will accompany the reconstruction results.

The replication package will include the frozen implementation, normalized reference models, crosswalks, exact configurations, source manifests, prompts, model identifiers, run outputs, alignment decisions, and analysis scripts. Source redistribution depends on the applicable permissions; URLs and retrieval scripts will accompany content hashes when texts cannot be shared. [TODO: add a working anonymous artifact link after the package is prepared.]

## 5. Results — Pending Evaluation

No outcome claims can be completed from the supplied archive. This section specifies the evidence required for the final paper.

### 5.1 RQ1: Expert recovery and evidence support

[TODO: report per-case, per-view decision P/R/F1; exact-option recall and precision; broader/narrower coverage; placement-aware recall; and grounding coverage/support.]

**Table 1 — main reconstruction results.** Rows: case × reference view × system. Columns: decision F1, exact-option recall, exact-option precision, placement-aware recall, supported-option coverage, and sampled evidence-support rate. Include the number of decisions/options behind each score.

[TODO: explain representative equivalent, merged, split, missed, and unsupported outputs using actual passages. Distinguish absences caused by unavailable sources where possible. Report expert ratings of unmatched items separately from raw reference agreement.]

### 5.2 RQ2: Baselines and component effects

[TODO: compare the full workflow with the long-context baseline and completed text-mining baselines. Report each case separately before drawing cross-case interpretations.]

**Table 2 — ablations.** For each implemented variant, show the change in exact-option recall, decision F1, supported-option coverage, and extraction tokens relative to the frozen full system. Include run variation and the actual number of successful runs.

[TODO: if the long-context baseline performs equally well or better, state that result directly. Attribute benefits to evidence, stability, or other measures only where those outcomes support the claim. Multiple removed stages in the TnT-inspired variant do not identify the causal contribution of any one stage.]

### 5.3 RQ3: Stability and resources

[TODO: provide per-case pairwise output agreement, model size distributions, tokens, runtime, and cost. Describe the settings controlling shuffle variation and model sampling.]

**Figure 3 — cost and coverage.** Show option recovery against passages processed for the stopping ablation, if intermediate outputs can be aligned consistently. Compare final coverage and consumed resources with complete-corpus runs. Do not interpret conceptual-coverage stopping as full theoretical saturation.

### 5.4 Supplementary Git-hosting case

[TODO: run the frozen system on independently segmented raw text. Keep the existing curated corpus as a sensitivity analysis because its headings and organization already encode design interpretations.]

[TODO: assess whether decision points admit coherent alternatives and whether supported placements distinguish the described systems. Unknown placements remain unknown. Empty cells do not establish invalid or novel combinations. Account for the single-label passage assignment limitation when producing a system × decision matrix.]

## 6. Discussion

Delve makes intermediate coding and revision artifacts part of architectural knowledge extraction. Their value must be established by the evaluation: decomposition may improve coverage and inspection, but it also introduces more model calls and additional opportunities for errors. The presence of a Critic does not guarantee better outputs, and passing a conceptual-coverage threshold does not guarantee completeness.

The important methodological distinction is between agreement with a reference model and usefulness for architectural reasoning. A reference may omit valid alternatives, while a generated model may reproduce its names without recovering the supporting argument. Conversely, a system may extract genuine options but group them too broadly to help an engineer make one choice. Reporting exact matching, granularity, placement, and grounding separately makes these outcomes visible.

Human review remains necessary for checking whether alternatives answer the same decision question, whether evidence supports the claimed scope, and whether relations express a meaningful architectural dependency. Between-run feedback offers a mechanism for correction, but improvement from that interaction remains unmeasured until a feedback study is completed. Similarly, automation cost cannot be equated with saved researcher effort without measuring corpus preparation, validation, and correction time.

[TODO: replace or extend these paragraphs with implications grounded in the completed findings.]

## 7. Threats to Validity

**Construct validity.** Expert models provide reference interpretations rather than exhaustive truth. Paper/model scope differences, uneven option descriptions, and granularity mismatches affect alignment. We retain both views, distinguish equivalent from partial coverage, and validate the matcher. Semantic provenance links may identify related text without supporting the extracted choice; grounding is assessed separately.

**Internal validity.** The development history includes exposure to both evaluated cases. A frozen rerun improves reproducibility but cannot undo this exposure. We will disclose affected settings and avoid held-out claims. Generator and critic models may share systematic biases, and a different-family evaluation judge still requires independent validation. Stopping, filtering, and consolidation can alter both recall and precision, motivating component comparisons.

**External validity.** Two studies from one research group provide limited diversity in modeling practices and domains. Hundreds of passages do not substitute for independent studies. The Git-hosting narrative adds a genre but does not supply comparable ground truth. Results will not establish effectiveness for arbitrary architectural documents, repository artifacts, or industrial design tasks.

**Reliability and conclusion validity.** Live-source drift, unavailable C2 sources, proprietary model changes, nondeterministic inference, and uncertain retrieval reproducibility can affect replication. Exact manifests and run artifacts mitigate but do not eliminate these issues. Small run counts limit statistical power, and repeated seeds measure within-case variation rather than generalization across domains.

**Training-data exposure.** Publication recency alone does not establish absence from training. A source-free reconstruction probe can reveal some prior knowledge, but failure to reconstruct a model does not prove absence of contamination. We will describe such probes as diagnostic evidence and avoid claims that C2 is contamination-free.

## 8. Conclusion

We presented Delve, a stateful agentic workflow for extracting architectural design spaces from practitioner literature. The workflow combines passage-level coding, iterative model revision, quality feedback, conceptual-coverage stopping, consolidation, and inspectable provenance links. Its methodological scope is an automated aid using grounded-theory techniques over a fixed corpus.

[TODO: insert one sentence stating the principal measured outcome and one sentence identifying the most consequential limitation.]

The proposed evaluation separates expert-model recovery, architectural grouping, evidence support, and resource use. These distinctions are necessary to assess whether workflow structure contributes useful architectural knowledge beyond what direct generation can provide.

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

### 9.1 What the supplied branch supports

| Statement | Evidence in the supplied archive | Draft treatment |
|---|---|---|
| Raw passage coding is available | `nodes/open_coder.py`; benchmark configs select `content` | Described as implemented |
| Source segmentation exists | `benchmark/build_corpus.py` | Described as implemented; generated corpora absent |
| Feedback and conceptual-coverage stopping exist | `graph.py`, `nodes/saturation_checker.py`, settings | Described with limited autonomy and saturation claims |
| Provenance linking exists | `nodes/evidence_linker.py` and consolidation integration | Described as inferred links requiring support validation |
| Verbatim evidence and paradigm-typed codes exist | Current `OpenCode` has id, label, rationale, status only | Excluded from current implementation claims |
| Drivers/impacts are first-class output fields | Absent from inspected output schemas | Deferred unless implemented and evaluated |
| Taxonomist uses validated editing tools | Separate plan explicitly marked proposed/not implemented | Excluded from current approach |
| Reference matching and experiment matrix are complete | No normalized `gt_paper.json`, `gt_model.json`, `gt_match.py`, or `run_matrix.py` found | Prospective evaluation, results pending |
| C1/C2 are untouched cases | Progress log describes pilot-driven fixes and calibration | Held-out wording removed |
| C2 has 29 recovered sources | Benchmark README reports 27/29 | Missing sources made explicit |
| Delve saves months of effort | No comparative human-effort measurements supplied | No such outcome claim |

The notes' initial abstract describes a planned enhanced system. Reconcile it with the frozen implementation before submission. If newer work exists outside this archive, incorporate it only after reviewing its code and run artifacts.

### 9.2 Minimum path to a defensible empirical submission

1. Decide the evaluated implementation and freeze its exact configuration. Preserve the history of C1/C2-informed tuning.
2. Materialize exact source texts and passage corpora; finish both expert-reference views and their crosswalks.
3. Implement and validate option/decision alignment and passage-support assessment. Resolve broader/narrower scoring and many-to-many grouping before analysis.
4. Run the full system and same-model long-context baseline first. Add feedback and consolidation ablations before expanding to optional drivers, human feedback, or extra cases.
5. Assemble the final results, anonymous artifacts, and figure traces from real outputs. Replace all prospective phrasing and `TODO` markers before submission.

This order is an editorial recommendation. It narrows the original plan's six questions and extensive ablation matrix to the strongest claims the current branch can support.

### 9.3 Suggested 10-page body allocation

| Material | Approximate pages |
|---|---:|
| Abstract and introduction | 1.0 |
| Background and related work | 1.0 |
| Approach and architecture/evidence figures | 2.0 |
| Benchmark and evaluation design | 2.0 |
| Results and main tables | 2.5 |
| Discussion, threats, conclusion | 1.5 |

The official track permits 10 pages plus up to 2 pages for references, requires double-anonymous review, and specifies IEEEtran conference format. Mandatory abstract deadline: **19 October 2026 AoE**. Paper deadline: **23 October 2026 AoE**. Verified 7 October 2026: https://conf.researchr.org/track/saner-2027/saner-2027-agentic-ai4se-track

### 9.4 Claims to settle before submission

- Choose between evaluating the current structured-revision workflow and completing the proposed tool-editing mechanism. Do not mix their descriptions.
- Treat intrinsic quality scores as control signals, not independent validation.
- Disclose pilot exposure without implying that a post-pilot freeze restores an untouched evaluation.
- Use evidence-support measurements for traceability claims. Existing passage IDs and similarity links alone do not justify “fully grounded.”
- Keep C3-curated sensitivity results separate from raw-text extraction because preorganization can encode the answer.
- Report provider/model settings as actually used. Names appearing in example configs have not been independently verified as callable production models.
- Measure human effort before claiming researcher-time savings; extraction API cost is a different outcome.

### 9.5 Draft provenance and remaining verification

This manuscript was prepared from the supplied planning notes and inspected source, configuration, benchmark documentation, and proposal files. External sources were consulted to verify track instructions, the C1 venue/date, and the short descriptions of cited text-mining and methodological work. The Zenodo records did not load during verification; their identifiers are preserved from the supplied materials without claiming independent verification of their complete contents. No API experiments, source retrieval, matcher calibration, or tests were run, and no repository implementation files were modified.
