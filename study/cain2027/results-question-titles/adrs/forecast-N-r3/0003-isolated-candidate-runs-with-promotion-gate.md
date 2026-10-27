# Isolated candidate runs with promotion gate

*How should model changes reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly run. Candidate models therefore need an isolated path to evaluation and promotion.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Small owning team

## Considered Options

* Isolated candidate runs with promotion gate
* Replace the production model directly

## Decision Outcome

Chosen option: "Isolated candidate runs with promotion gate".

Isolated candidate runs let the three-person team iterate while keeping the weekly production pipeline on its current model until a replacement is ready.

### Consequences

* Promotion criteria and ownership must be defined.
* Production model versions need to be recorded per run.

## Pros and Cons of the Options

### Isolated candidate runs with promotion gate

* Good, because Separates experiments from production
* Good, because Allows checks before promotion
* Bad, because Requires promotion workflow
* Bad, because Adds candidate-run compute

### Replace the production model directly

* Good, because Few deployment steps
* Bad, because Experiments can disrupt runs
* Bad, because Harder to compare versions
