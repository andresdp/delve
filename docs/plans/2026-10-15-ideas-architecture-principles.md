---
title: "ideas: architecture principles as guardrails for mining design spaces (parked)"
type: ideas
status: parked (2026-10-15); idea 2 (vocabulary) is used now, ideas 1, 3, 4 later
date: 2026-10-15
related: >-
  papers/Woods-Architecture-Principles.pdf (local, not tracked),
  docs/plans/2026-10-15-feat-value-exclusivity-plan.md, docs/plans/2026-10-15-feat-value-recoding-plan.md
---

# Architecture principles as guardrails

## Source

E. Woods, "Harnessing the Power of Architectural Design Principles" (practitioner column; venue and year to
confirm before citing it). It builds on N. Rozanski and E. Woods, *Software Systems Architecture*, 2nd ed.,
Addison-Wesley, 2011, and D. Greefhorst and E. Proper, *Architecture Principles*, Springer, 2011.

- **Principle:** "a declarative statement that normatively prescribes a property of the design of an artefact,
  which is necessary to ensure that the artefact meets its essential requirements" (Greefhorst and Proper).
- **Template:** name, description (often an ordered preference: (1) industry standard, (2) organisational
  standard, (3) published application format), applicability, rationale.
- **A good principle is** constructive, reasoned, well articulated, testable and significant (Rozanski and
  Woods). Significance test: *could the opposite statement ever be true?* If not, it is a truism.
- **Violations are information:** a justified violation reveals something about the system; routine
  violations mean the principle should change.

The column is experience and opinion, not a study: it motivates and names, it does not validate.

## The five criteria applied to a decision point

| Criterion | For a decision point | Delve |
|---|---|---|
| Constructive | guides a real decision | one decision point, ≥ 2 candidate decisions (selection) |
| Reasoned | motivated by drivers and goals | use-case relevance; outcomes and `affects` relations |
| Well articulated | clear to its stakeholders | Critic's clarity criterion |
| Testable | one can check which alternative a system took | **exclusivity** (value exclusivity row; value recoding) |
| Significant | the alternatives are real choices, not truisms | not covered: idea 1 |

Used now (idea 2): this vocabulary frames exclusivity and value recoding in the paper (§3.5).

## Parked ideas

### 1. Significance check for candidate decisions

Values such as *automated deployment and rollback* or *reliable monitoring* are often truisms or goals: nobody
would choose their opposite, so they are not alternatives ("Axis vs. value" scores 0.2–0.5). Apply Woods' test,
*within the use case*: is the opposite a reasonable choice for a system in scope?

- As a judged scoreboard criterion ("Significance"), so the loop's feedback pushes against truisms.
- As a pass after evidence linking, like the rehome pass: one call per dimension, failing values become
  outcomes (kept, not deleted) or are flagged.
- Expected side effect: higher exclusivity, since a truism is adopted by almost every source.
- Risk: over-pruning practices that were real options in their context (e.g. "use CI" in early MLOps).
- Evaluation: offline estimate on the saved C1/C2 runs, then replay and match with the independent matcher, as
  for value recoding.

### 2. (in use) Vocabulary for "architecturally relevant"

See the table above.

### 3. Mined principles as an output

Per-source stances (accepted / rejected / mixed) give preference patterns: "When ⟨applicability⟩, prefer A,
then B; ⟨rationale from passages⟩". Sources adopting a less preferred option, with their reasons, are the
justified violations. Output: a wiki page *Principles*, `ddspace query principles`, an agent-facing summary.
Deterministic preference orders, one LLM call per principle for the wording. The "contested" synthesis page is
the closest existing piece.

### 4. User principles as guardrails

Principles listed in `ddspace.yaml` (name, description, applicability, rationale). Selection uses them to judge
relevance; the wiki flags candidate decisions that conflict with them; agents receive them in `AGENTS.md`.
Useful for teams, not for the study.
