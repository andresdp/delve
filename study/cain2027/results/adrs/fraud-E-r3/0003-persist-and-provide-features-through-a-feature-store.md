# Persist and provide features through a feature store

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring needs access to transaction features, and auditors need to know which features produced each score. The brief does not prescribe a storage technology.

## Decision Drivers

* Feature access
* Auditability
* Low latency

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

A feature store is the closest available design-space choice for managed feature access. The brief’s latency and audit requirements still require the store’s serving path and feature snapshot behavior to be specified.

### Consequences

* Provide a low-latency feature lookup path.
* Record the feature values or immutable feature references used for each score.

## Pros and Cons of the Options

### Feature store

* Good, because Dedicated feature access
* Good, because Central feature management
* Bad, because Additional system to operate
* Bad, because Specific design unspecified
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Use existing stores
* Good, because Fewer specialized components
* Bad, because Feature access conventions needed
* Bad, because Consistency work
* Sources: `d:4`, `v:4.2`
