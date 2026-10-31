# Separate candidate evaluation and promotion

*How should model ideas reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly run. Candidate models therefore need a separate evaluation path before replacing the production model.

## Decision Drivers

* Rapid model iteration
* Protect weekly run
* Small team

## Considered Options

* Separate candidate evaluation and promotion
* Edit production pipeline directly

## Decision Outcome

Chosen option: "Separate candidate evaluation and promotion".

Evaluating candidates separately lets the team iterate while keeping the weekly production path stable until a candidate is ready.

### Consequences

* Candidate and production paths must share documented inputs.
* Promotion criteria and rollback need implementation.

## Pros and Cons of the Options

### Separate candidate evaluation and promotion

* Good, because Isolates experiments
* Good, because Controlled rollout
* Bad, because Adds evaluation workflow
* Bad, because Requires promotion criteria

### Edit production pipeline directly

* Good, because Few components
* Good, because Fast initial changes
* Bad, because Experiments affect run
* Bad, because Harder to recover
