# Isolate model experiments from the weekly production run

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without disrupting the weekly run. Experiments therefore need a separate path to evaluation and promotion.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Three-person team

## Considered Options

* Separate experiment and production paths with promotion
* Replace the production model in place

## Decision Outcome

Chosen option: "Separate experiment and production paths with promotion".

A promotion path lets the team test new ideas while keeping the scheduled production run stable.

### Consequences

* Candidate models need evaluation before promotion.
* The production model version must be tracked per run.

## Pros and Cons of the Options

### Separate experiment and production paths with promotion

* Good, because Limits run disruption
* Good, because Enables controlled comparison
* Bad, because Requires promotion steps
* Bad, because Maintains separate configurations

### Replace the production model in place

* Good, because Few process steps
* Good, because Fast code changes
* Bad, because Experiments can break runs
* Bad, because Harder to compare models
