# How should model ideas reach production?

* System: Retail demand forecasting

## Context and Problem Statement

The team wants new model ideas in production quickly without breaking the weekly forecast run.

## Decision Drivers

* Weekly run reliability
* Fast model iteration
* End-to-end ownership

## Considered Options

* Promote models through validation and staged release
* Replace the production model directly

## Decision Outcome

Chosen option: "Promote models through validation and staged release".

Weekly run reliability is the deciding driver; staged validation costs some release speed but reduces the chance that experiments disrupt the scheduled run.

### Consequences

* A validation and promotion process must be maintained.
* Production needs a known-good model fallback.

## Pros and Cons of the Options

### Promote models through validation and staged release

* Good, because Weekly run reliability: validate before promotion
* Good, because Fast model iteration: parallel candidate evaluation
* Bad, because Fast model iteration: promotion adds a step

### Replace the production model directly

* Good, because Fast model iteration: shortest path to production
* Bad, because Weekly run reliability: unvalidated changes can break runs
