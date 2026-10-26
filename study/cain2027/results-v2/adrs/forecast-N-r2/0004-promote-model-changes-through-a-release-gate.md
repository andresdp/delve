# Promote model changes through a release gate

* System: Retail demand forecasting

## Context and Problem Statement

The team wants new model ideas in production quickly without breaking the weekly run. A candidate should be evaluated before it replaces the production model.

## Decision Drivers

* Weekly run reliability
* Fast model iteration
* Historical reproducibility

## Considered Options

* Evaluate candidate, then promote
* Replace production model directly

## Decision Outcome

Chosen option: "Evaluate candidate, then promote".

Weekly run reliability decides the choice, while isolated candidate evaluation still supports iteration; the cost is a promotion step before release.

### Consequences

* Maintain a known-good production model.
* Record the promoted model version with each run.

## Pros and Cons of the Options

### Evaluate candidate, then promote

* Good, because Weekly run reliability: keep known-good model
* Good, because Fast model iteration: test candidates independently
* Bad, because Fast model iteration: evaluation adds a step

### Replace production model directly

* Good, because Fast model iteration: shortest path to production
* Bad, because Weekly run reliability: unproven change risk
* Bad, because Historical reproducibility: weaker release trace
