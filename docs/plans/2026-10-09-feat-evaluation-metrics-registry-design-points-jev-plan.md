---
title: "feat: configurable evaluation metrics, design-point metric, Jev scoring and graph decisions"
type: feat
status: planned (not started; brainstorm 2026-10-09)
date: 2026-10-09
related: >-
  config.yaml (evaluation:), src/taxonomy_generator/evaluation/{metrics,runner,judge,design_points}.py,
  src/taxonomy_generator/nodes/{taxonomy_evaluator,saturation_checker,value_consolidator,dimension_merger,dimension_selector}.py,
  src/taxonomy_generator/configuration.py, src/taxonomy_generator/utils.py (format_evaluation_summary)
---

# Configurable evaluation metrics, a design-point metric, and Jev

## Goal

Three related lines of work on the LLM-as-judge evaluation, plus one extension:

1. **Metric registry:** every evaluation metric can be enabled or disabled in the YAML; future metrics plug in the same way.
2. **Design-point metric:** sample design points from the mined space and assess them against the sources. Usable both
   as a run quality criterion (in the loop or on the final view) and as an offline analysis only.
3. **Jev scoring:** re-implement the critic's criteria so that the evaluator owns the criteria and Jev only returns
   scores; the loop's feedback is the criteria plus the computed scores.
4. **Jev decisions in the graph:** use Jev for bounded decisions inside the LangGraph pipeline, to make runs faster.

## Current state (2026-10-09)

- **Critic:** 8 structural criteria plus 2 document-grounded coverage criteria
  (`evaluation/metrics.py`), each a DeepEval `GEval` with fixed evaluation steps, on OpenAI (`judge.py`; gpt-5.6-luna).
  Run every N drafts and on the final view (`evaluate_taxonomy`, `evaluate_taxonomy_final` nodes). The judge's
  generated reasons feed the next update/review (`utils.format_evaluation_summary`) except criteria in
  `feedback_exclude`.
- **YAML switches today:** `evaluation.enabled`, coverage on/off, `feedback_exclude`, `every_n_iterations`,
  `max_documents`, `threshold` (display only). No per-criterion on/off.
- **Offline analyses with their own settings/scripts:** GT matcher (`--match-gt`), consistency, quality probe,
  stage funnel, design-point sampler (A12, `evaluation/design_points.py`, attestation by system on C3).
- **DeepEval installed:** 4.1.8 (no `JevEval`); PyPI latest 4.2.8. Version that adds `JevEval`: to confirm.

## Jev facts (from the DeepEval and LangChain posts)

- Sources: https://deepeval.com/blog/introducing-jev-as-a-judge, https://deepeval.com/docs/metrics-jev-eval,
  https://www.langchain.com/blog/jev-agent-evals-langsmith
- Jev is a decision model, not a generator: bounded questions return probabilities.
  - `Noul`: yes/no proposition → P(true).
  - `Score`: ordered scale (worst → best) → expected position in [0, 1].
  - `Choice`: unordered options with credits → weighted probability in [0, 1].
- DeepEval wrapper: `JevEval(name, evaluation_params, questions, threshold, strict_mode, async_mode, include_reason, …)`;
  score = fixed weighted mean of the question values; `score_breakdown` per question (probability, confidence,
  applicability); `reason` is deterministic text built from the probabilities.
- Access: hosted TypeSafe API only (`TYPESAFE_API_KEY`; `pip install typesafe-sdk`). LangChain integration package:
  `langchain-typesafe` (alpha). The user has a key (2026-10-09).
- Claims (narrow test, 5 runs of one agent): about $0.00035 per call, about 0.44 s, far lower variance than LLM judges.
  The post warns that a cheap, consistently wrong evaluator amplifies mistakes: calibration is required.

## 1. Metric registry (YAML on/off)

Sketch:

```yaml
evaluation:
  enabled: true
  backend: geval              # geval | jev
  every_n_iterations: 3
  metrics:
    orthogonality:            {enabled: true}
    completeness:             {enabled: true, feedback: false}   # replaces feedback_exclude
    dimensional_coverage:     {enabled: true}
    design_point_coherence:   {enabled: false, when: loop}
    design_point_grounding:   {enabled: false, when: final, n: 20, k: [2, 3]}
```

Per-metric fields: `enabled`, `feedback` (reasons/scores reach the next update), `when` (`loop` | `final` | `offline`),
optional `backend` override, metric-specific parameters.

Decisions:
- Backward compatible: no `metrics:` block → today's behavior; `feedback_exclude` and the coverage switch map onto it.
- Each scoreboard records the metric set, backend and versions, so scores from different sets are never compared by
  accident.
- Disabling a fed-back metric changes the run (not only the report): record it in the run record (P13); this is how the
  ablations (P12) would switch criteria.
- Scope: judge-style metrics and the design-point metric. The matcher, consistency and probe keep their own settings for
  now (they could later join with `when: offline`).

Effort: about 1 day.

## 2. Design-point metric

Question: are the design points the space allows real or reasonable designs according to the sources? Judges the
space as a whole, which no current criterion does.

| Variant | Scoring | LLM/Jev cost | When |
|---|---|---|---|
| a. Attestation rate | share of sampled points whose values are all supported by one source / passage (C3: one system) | none | final, offline |
| b. Coherence | can these choices coexist in one design? (no evidence needed) | one Jev `Noul`/`Score` per point | loop or final |
| c. Grounding | given each value's supporting passages, is each choice supported and the combination plausible? | one call per point | final (needs evidence links) |
| d. Constraint check | does a point violate a `constrains` relation? | low | after the relations redesign (P17) |
| e. System recovery (C3) | can each system be placed as a point; are different systems different points? | none to low | offline |

- **As a quality criterion:** coherence (b) can run in the loop on drafts; with Jev it is cheap enough per point.
  Feedback names the dimension pairs that produce incoherent points (dimensions not independent, or values that are
  outcomes). Grounding (c) and attestation (a) run on the final view, because evidence links exist only at the end.
- **As an analysis only:** the same code with `when: offline`, over saved runs (C1, C2, C3).
- **Validity controls (must pass before use):** attested > random > broken points (values shuffled across dimensions,
  two values from one dimension); stable across sampler seeds; fixed seed and n per run (as the coverage sample).

Effort: offline prototype 1–1.5 days, then the registry entry.

## 3. Jev scoring for the critic

Design (user decision, 2026-10-09): **the evaluator owns the criteria; Jev only scores.**

- Each criterion becomes an evaluator class holding its criterion text and a set of bounded Jev questions, ideally
  **per item** (per dimension, per value) rather than one score for the whole taxonomy. Examples:
  - One decision point: per dimension, `Noul` "This dimension asks exactly one question that requires a choice."
  - Axis vs. value: per value, `Choice` {alternative answer, outcome/effect, a separate decision, unrelated}.
  - No catch-alls: per value, `Noul` "This value is a catch-all (other, misc, combinations)."
  - Orthogonality: per dimension pair from a candidate shortlist (embedding distance), `Noul` "These two dimensions
    ask the same question."
  - Clarity: per dimension, `Score` ambiguous → clear.
  - Coverage: per sampled passage, `Noul` "The design decision in this passage maps to a dimension of the taxonomy."
- The criterion score aggregates the item scores (e.g. mean, or share above a cutoff) in our code.
- **Feedback to the graph:** the criterion text plus the computed scores, listing the lowest-scoring items by name
  (e.g. "One decision point: 0.62. Lowest: 'Deployment and monitoring' 0.21, …"). Deterministic and actionable
  without generated reasons. Optional hybrid: ask the LLM to explain only the few lowest items.
- Backend switch per metric (`backend: geval | jev`); GEval stays as the reference.
- Implementation: either DeepEval `JevEval` (needs a DeepEval upgrade) or the TypeSafe SDK directly; pick after the
  spike. Wrap it in one `jev_client` module (retries, batching, caching like the matcher's judge cache, opt-out of
  telemetry).

## 4. Jev for decisions inside the graph

Candidates: bounded LLM decisions in today's nodes (to verify one by one; each must keep a GEval/LLM fallback):

| Node | Decision | Jev question type |
|---|---|---|
| `saturation_checker` | does an open code of the new minibatch fall outside the taxonomy? (drives the stop rule) | `Noul` per concept |
| `dimension_merger` | are two borderline dimensions the same decision? | `Noul` per pair |
| `value_consolidator` | are two borderline values the same alternative? | `Noul` / `Choice` per pair |
| `dimension_selector` (relevance filter) | does a dimension serve the use case? | `Noul` per dimension |
| stance at evidence linking / open coding | accepted / rejected / mixed | `Choice` |
| conditional edges (`should_continue_*`) | already rule-based on scores; Jev scores would feed them | – |

Not candidates: generative steps (open coding, taxonomy drafting and updates, labeling text, reports).

**Independence caveat:** if Jev makes decisions inside the graph and also judges its output, the evaluation is no
longer independent of the generator. Keep the GT matcher's judge and the paper's evaluation on a different model
than any in-graph Jev decision, or state it as a limitation.

## Roadmap

| Step | What | Effort | Depends on |
|---|---|---|---|
| R0 | Measure the evaluation's share of run tokens and time (saved runs); re-score one draft 3× with GEval for noise | 0.5 day | – |
| R1 | Metric registry and YAML switches (§1) | 1 day | – |
| R2 | Replay harness: re-score saved drafts (`evaluation_history`) with any backend and metric set, no pipeline run | 0.5–1 day | R1 |
| R3 | Jev spike: client module, 2–3 criteria as per-item questions, compared with GEval via R2 | 1 day | R2, Jev access, DeepEval upgrade or SDK |
| R4 | Design-point metric: offline prototype with controls (§2), then registry entries (loop coherence, final grounding) | 1.5–2 days | R1 (R3 for the Jev variant) |
| R5 | Jev critic for all criteria, feedback = criteria + scores (§3); A/B a full run against GEval | 1–2 days | R3 results |
| R6 | Jev decisions in the graph (§4), one node at a time, each A/B'd offline then in one run | 0.5–1 day per node | R3 |

**Comparison protocol for R3, R5, R6** (paired, same drafts or same inputs):
- agreement with GEval per criterion (rank correlation) and with the GT results on C1/C2 where they apply;
- variance across repeated scoring;
- latency and cost per scoreboard / per decision;
- for graph decisions: agreement with the current LLM decision on logged inputs, and the downstream effect on the
  run (dimensions, matcher scores) in one paired run;
- calibration against human labels where available (A6 sheet) before any switch becomes the default.

**Timing:** the paper deadline (2026-10-23) comes first. R0 is useful now; R1 only if the ablations (P12) need it;
the rest after submission.

## Environment (conda env `taxonomy`; no new environment)

To verify at R3, not installed yet:
- `pip install -U "deepeval>=<version with JevEval>"` (installed 4.1.8; check that the GEval code still works);
- `pip install typesafe-sdk` (and `langchain-typesafe` only if using the LangChain integration);
- `TYPESAFE_API_KEY` in `.env`.

## Open questions

- Which DeepEval version introduced `JevEval`; does the upgrade change GEval behavior (scores must stay comparable)?
- Per-item questions multiply calls (e.g. 30 dimensions × 8 criteria): batching limits and rate limits of the Jev API.
- Data egress: the coverage and grounding variants send corpus passages (from downloaded, copyrighted source texts) to
  TypeSafe. The user has a Jev key; confirm that sending passages is acceptable, otherwise limit Jev to structural
  criteria (taxonomy only).
- Does deterministic score-only feedback steer the Taxonomist as well as GEval's generated reasons? (R5 A/B.)
