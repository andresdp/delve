# Validate model changes before the weekly production run

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly run. A separate validation step can check candidate changes before they affect production forecasts.

## Decision Drivers

* Weekly-run reliability
* Fast model iteration
* Forecast reproducibility

## Considered Options

* Validate candidates on historical weeks before promotion
* Replace the production model directly

## Decision Outcome

Chosen option: "Validate candidates on historical weeks before promotion".

Weekly-run reliability decides the choice: candidate models are checked before promotion, reducing the chance that an experiment disrupts production. This gives up some deployment speed for the validation step.

### Consequences

* Historical evaluation data and acceptance criteria must be maintained.
* Promoted model versions must be recorded with production runs.

## Pros and Cons of the Options

### Validate candidates on historical weeks before promotion

* Good, because Weekly-run reliability: candidate failures stay out of production
* Good, because Fast model iteration: supports repeatable candidate evaluation
* Bad, because Fast model iteration: validation adds a promotion step

### Replace the production model directly

* Good, because Fast model iteration: shortest path to production
* Bad, because Weekly-run reliability: candidate changes can break the run
* Bad, because Forecast reproducibility: unrecorded changes complicate reruns
