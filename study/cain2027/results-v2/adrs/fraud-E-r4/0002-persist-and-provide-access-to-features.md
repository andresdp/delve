# Persist and provide access to features

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to know which features produced each score, and the serving path has a tight latency budget. The design space identifies a feature store and general-purpose data stores as alternatives (d:4).

## Decision Drivers

* Audit traceability
* Scoring latency

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

Audit traceability decides in favor of a feature store; its added serving lookup must fit within the latency budget.

### Consequences

* Record the feature values or immutable references used for each score.
* Feature lookup latency becomes part of the scoring path.

## Pros and Cons of the Options

### Feature store

* Good, because Audit traceability: dedicated feature access
* Bad, because Scoring latency: extra storage service may add a lookup
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Scoring latency: can use an existing serving store
* Bad, because Audit traceability: feature lineage needs separate handling
* Sources: `d:4`, `v:4.2`
