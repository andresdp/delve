# Feature store

*How should features be persisted and accessed?*

* System: Card-fraud scoring service

## Context and Problem Statement

Online scoring needs transaction features available at request time, and audit review needs the inputs associated with each score. The design space presents a feature store or general-purpose data stores (d:4).

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability
* Audit traceability

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

Latency decides: consistent online feature access best serves the transaction path, while centralized definitions help preserve audit context. This adds a storage dependency to the scoring path.

### Consequences

* Feature-store availability is part of scoring availability.
* Feature values used for each score need to be recorded for audit.

## Pros and Cons of the Options

### Feature store

* Good, because Latency: purpose-built feature access
* Good, because Traceability: central feature definitions
* Bad, because Availability: adds a serving dependency
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Availability: use existing storage
* Bad, because Latency: access patterns may vary
* Bad, because Traceability: feature definitions can diverge
* Sources: `d:4`, `v:4.2`
