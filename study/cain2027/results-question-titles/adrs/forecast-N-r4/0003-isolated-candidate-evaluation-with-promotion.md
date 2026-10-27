# Isolated candidate evaluation with promotion

*How should new model ideas reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

The three data scientists own the pipeline end to end and want model ideas to reach production quickly without breaking the weekly run. Isolating candidate evaluation from the production forecast path allows both goals to be addressed.

## Decision Drivers

* fast model iteration
* protect weekly run
* team of three

## Considered Options

* Isolated candidate evaluation with promotion
* Edit production model directly
* Separate experimentation platform

## Decision Outcome

Chosen option: "Isolated candidate evaluation with promotion".

Evaluate candidate models on historical weeks using the same data and metrics as the current production model, then promote a selected candidate through a controlled change. This keeps experimentation close to the existing pipeline while limiting risk to the weekly run.

### Consequences

* Keep candidate evaluation separate from production publishing.
* Define shared evaluation data and metrics.
* Provide a rollback path to the previous model.

## Pros and Cons of the Options

### Isolated candidate evaluation with promotion

* Good, because production stays stable
* Good, because comparable candidates
* Bad, because promotion workflow needed
* Bad, because evaluation adds time

### Edit production model directly

* Good, because few process steps
* Good, because fastest initial change
* Bad, because weekly run exposed
* Bad, because hard to compare

### Separate experimentation platform

* Good, because strong isolation
* Good, because rich experimentation
* Bad, because higher operating cost
* Bad, because team overhead
