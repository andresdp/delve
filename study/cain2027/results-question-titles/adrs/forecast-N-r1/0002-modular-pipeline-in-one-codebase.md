# Modular pipeline in one codebase

*How should data and pipeline steps be organized?*

* System: Retail demand forecasting

## Context and Problem Statement

A team of three data scientists owns the pipeline end to end. Its steps need to be understandable and maintainable by that team.

## Decision Drivers

* Small owning team
* End-to-end ownership
* Weekly run

## Considered Options

* Modular pipeline in one codebase
* Independent services

## Decision Outcome

Chosen option: "Modular pipeline in one codebase".

A modular codebase keeps the pipeline cohesive for a small team while allowing data preparation, training, and forecasting logic to evolve separately.

### Consequences

* Modules share a release process.
* Interfaces between pipeline stages need to be maintained.

## Pros and Cons of the Options

### Modular pipeline in one codebase

* Good, because Shared conventions
* Good, because Simple coordination
* Bad, because Shared release boundary
* Bad, because Modules need clear ownership

### Independent services

* Good, because Separate deployments
* Good, because Independent scaling
* Bad, because More operational overhead
* Bad, because Cross-service coordination
