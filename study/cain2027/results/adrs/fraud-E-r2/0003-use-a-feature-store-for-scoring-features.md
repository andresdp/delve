# Use a feature store for scoring features

* System: Card-fraud scoring service

## Context and Problem Statement

The score must be explainable later by identifying the features used to produce it. The brief does not prescribe how features are stored or accessed.

## Decision Drivers

* Feature traceability
* Low-latency access

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

A feature store is the available alternative specifically for persisting and providing feature access. Pairing it with score records supports later feature-level review, though the design space does not specify the required audit record format.

### Consequences

* Feature retrieval becomes a serving dependency.
* Retain the exact feature values used for each score.

## Pros and Cons of the Options

### Feature store

* Good, because Central feature access
* Good, because Feature-specific support
* Bad, because Additional component
* Bad, because Operational dependency
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Use existing stores
* Good, because Fewer specialized components
* Bad, because Feature access conventions needed
* Bad, because Harder consistency
* Sources: `d:4`, `v:4.2`
