# What should be recorded for audit?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later establish which model version and features produced any score. The record must link the scoring result to those inputs and the transaction.

## Decision Drivers

* Auditable model version
* Auditable feature inputs

## Considered Options

* Persist score and inference snapshot
* Persist model version and feature references

## Decision Outcome

Chosen option: "Persist score and inference snapshot".

Persisting the actual model version and feature values directly addresses the stated audit question. It costs more storage, but avoids relying on mutable or unavailable references later.

### Consequences

* Each score needs a durable audit record.
* Retention, access control, and sensitive-feature handling need policies.

## Pros and Cons of the Options

### Persist score and inference snapshot

* Good, because Reconstructs scoring inputs
* Good, because Supports audit queries
* Bad, because Storage and retention cost
* Bad, because Write path needs reliability

### Persist model version and feature references

* Good, because Smaller records
* Good, because Can reuse feature store
* Bad, because References may expire
* Bad, because Reconstruction may vary
