# Keep an auditable record for every score

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to reconstruct which model version and features produced a transaction score after the live request has completed.

## Decision Drivers

* Later audit
* Model attribution
* Feature attribution

## Considered Options

* Durable per-score audit records
* Operational logs only

## Decision Outcome

Chosen option: "Durable per-score audit records".

A durable record can retain the score, model version, and feature snapshot for later auditor review.

### Consequences

* Audit writes add work to the scoring path or a downstream path.
* Retention and lookup behavior must be defined.

## Pros and Cons of the Options

### Durable per-score audit records

* Good, because Supports later lookup
* Good, because Decouples audit from live serving
* Bad, because Adds write and retention costs

### Operational logs only

* Good, because Uses existing telemetry path
* Bad, because Records may be incomplete or short-lived
