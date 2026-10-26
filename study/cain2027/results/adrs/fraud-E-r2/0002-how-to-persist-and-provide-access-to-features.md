# How to persist and provide access to features?

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring service needs transaction features, and auditors must later identify which features produced each score.

## Decision Drivers

* Feature traceability
* Online scoring

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

A feature store is the dedicated feature persistence and access option in the design space (d:4, v:4.1). The brief's audit requirement favors a deliberate feature access layer, though the space does not establish its audit capabilities.

### Consequences

* Operate a feature store alongside scoring.
* Record feature values or a reproducible feature reference for each score.

## Pros and Cons of the Options

### Feature store

* Good, because Dedicated feature access
* Bad, because Additional system to operate
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Uses existing stores
* Bad, because Feature access conventions unspecified
* Sources: `d:4`, `v:4.2`
