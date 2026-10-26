# How should score inputs and model identity be auditable?

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires later identification of the model version and features that produced each score. That requires a durable record linking each scoring event to its inputs and result.

## Decision Drivers

* Feature traceability
* Model version traceability
* Auditor review

## Considered Options

* Persist per-score audit record
* Keep aggregate service logs only

## Decision Outcome

Chosen option: "Persist per-score audit record".

A per-score record can associate the model version, features, and score for each transaction, matching the auditor requirement.

### Consequences

* Audit writes must fit latency and availability needs.
* Feature representation and retention need definition.

## Pros and Cons of the Options

### Persist per-score audit record

* Good, because Direct event-to-input linkage
* Good, because Supports later review
* Bad, because Storage and retention cost
* Bad, because Write-path overhead

### Keep aggregate service logs only

* Good, because Lower storage volume
* Good, because Simpler logging
* Bad, because Cannot reliably reconstruct inputs
* Bad, because Weak score-level traceability
