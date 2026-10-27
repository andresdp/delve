# Feature persistence and access

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring service needs features during a live transaction, and auditors need to know which features contributed to a score.

## Decision Drivers

* Fast feature access
* Feature traceability
* Training and serving consistency

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

A feature store provides a dedicated feature access choice, which suits the need to identify the inputs behind each score. Its lookup latency must fit within the online scoring budget.

### Consequences

* Capture the feature values or an immutable feature reference per score.
* Keep online feature retrieval within the latency budget.

## Pros and Cons of the Options

### Feature store

* Good, because Central feature access
* Good, because Feature-specific support
* Bad, because Additional operational dependency
* Bad, because Lookup latency
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Uses existing stores
* Good, because Fewer specialized components
* Bad, because Feature access conventions needed
* Bad, because Consistency work
* Sources: `d:4`, `v:4.2`
