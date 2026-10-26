# Feature persistence and access

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring path needs features for each transaction, and the audit record must identify which features produced each score. The brief does not specify feature freshness or access patterns.

## Decision Drivers

* Online feature access
* Feature traceability

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

Choose a feature store as a dedicated place to retrieve scoring features and support feature traceability. The design space does not establish that it meets the service latency budget, so confirm that in implementation. (d:4, v:4.1)

### Consequences

* Record feature identities or snapshots with each score.
* Feature lookup latency becomes part of the request budget.

## Pros and Cons of the Options

### Feature store

* Good, because Dedicated feature access
* Good, because Central feature management
* Bad, because Additional component
* Bad, because Operational dependency
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Uses existing stores
* Good, because Fewer ML components
* Bad, because Feature logic distributed
* Bad, because Consistency needs design
* Sources: `d:4`, `v:4.2`
