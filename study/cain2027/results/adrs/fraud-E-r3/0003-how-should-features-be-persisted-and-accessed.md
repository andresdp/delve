# How should features be persisted and accessed?

* System: Card-fraud scoring service

## Context and Problem Statement

Feature values contribute to each transaction score, and auditors need to identify which features produced it. A feature store is a candidate for providing a consistent access layer.

## Decision Drivers

* feature-level traceability
* low-latency access
* auditor review

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

A dedicated feature access layer is a reasonable fit for traceable scoring, though the design space does not specify its latency or audit capabilities. (d:4, v:4.1)

### Consequences

* Feature reads add a dependency to online scoring.
* Record feature values or immutable references with each score.

## Pros and Cons of the Options

### Feature store

* Good, because dedicated feature access
* Good, because centralized feature management
* Bad, because additional component
* Bad, because operational overhead
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because uses existing stores
* Good, because fewer dedicated components
* Bad, because feature access conventions needed
* Bad, because lineage may be harder
* Sources: `d:4`, `v:4.2`
