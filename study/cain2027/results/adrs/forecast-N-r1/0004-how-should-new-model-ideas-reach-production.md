# How should new model ideas reach production?

* System: Retail demand forecasting

## Context and Problem Statement

The team wants to move new model ideas to production quickly without breaking the weekly run. Experimental work therefore needs a separate path from the production forecast run.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Small team

## Considered Options

* Isolated experiments with explicit promotion
* Edit production pipeline directly

## Decision Outcome

Chosen option: "Isolated experiments with explicit promotion".

Isolated experiments let the team try model ideas independently; explicit promotion gives production a controlled change point that protects the weekly run.

### Consequences

* Experiments need a separate execution path.
* Promotion criteria and ownership must be defined.

## Pros and Cons of the Options

### Isolated experiments with explicit promotion

* Good, because Protects scheduled run
* Good, because Supports quick trials
* Bad, because Needs promotion checks
* Bad, because Duplicates some compute

### Edit production pipeline directly

* Good, because Few deployment steps
* Good, because Immediate changes
* Bad, because Can disrupt weekly run
* Bad, because Harder experiment comparison
