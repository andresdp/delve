# Feature store

*How to persist and provide access to features?*

* System: Card-fraud scoring service

## Context and Problem Statement

Each score depends on features, and auditors need to know which features produced it. The design space offers a feature store or general data stores (d:4).

## Decision Drivers

* feature traceability
* online latency

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

A feature store is the better fit for controlled feature access; log the feature values or immutable feature references used for each score to meet audit needs (d:4, d:22).

### Consequences

* Keep online feature reads within the scoring latency budget.
* Retain feature values or reproducible references with each score.

## Pros and Cons of the Options

### Feature store

* Good, because Feature-specific access
* Good, because Centralized feature handling
* Bad, because Added infrastructure
* Bad, because Operational dependency
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Fewer specialized systems
* Good, because Existing storage
* Bad, because Scattered access patterns
* Bad, because Harder consistency
* Sources: `d:4`, `v:4.2`
