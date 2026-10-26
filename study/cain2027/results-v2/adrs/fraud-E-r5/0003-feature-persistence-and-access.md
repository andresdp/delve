# Feature persistence and access

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to identify the features used for each score. The design space covers feature access and persistence choices (d:4), but does not specify audit record contents.

## Decision Drivers

* Auditability
* Tens-of-milliseconds latency

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

Auditability decides: a feature store provides a central point for feature access, at the cost of an additional lookup in the scoring path. This choice appeared in the checked combination, which had no warnings and no attesting sources.

### Consequences

* Feature lookup latency must fit the score deadline.
* Feature values and versions need to be recorded for audit.

## Pros and Cons of the Options

### Feature store

* Good, because Auditability: central feature access point
* Bad, because Low latency: feature lookup adds a dependency
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Low latency: direct access to existing stores
* Bad, because Auditability: feature lineage may be fragmented
* Sources: `d:4`, `v:4.2`
