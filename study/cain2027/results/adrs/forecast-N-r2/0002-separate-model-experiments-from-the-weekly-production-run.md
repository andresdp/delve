# Separate model experiments from the weekly production run

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly run. A three-person team also needs a small, understandable path from experimentation to production.

## Decision Drivers

* Fast model iteration
* Reliable weekly run
* Small team ownership

## Considered Options

* Promote candidates through an isolated evaluation step
* Replace the production model directly

## Decision Outcome

Chosen option: "Promote candidates through an isolated evaluation step".

An evaluation step allows the team to try candidates independently and promote only a selected model. This balances iteration speed with continuity of the weekly forecast.

### Consequences

* Candidate and production models need distinct versions.
* Promotion adds an explicit workflow step.

## Pros and Cons of the Options

### Promote candidates through an isolated evaluation step

* Good, because Protects scheduled run
* Good, because Enables comparable evaluation
* Bad, because Requires promotion workflow
* Bad, because Adds candidate tracking

### Replace the production model directly

* Good, because Few workflow steps
* Good, because Fastest initial rollout
* Bad, because Experiments can disrupt runs
* Bad, because Harder to compare models
