# Record the model version and feature values with each score

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires later audit of both the model version and the features used. Persisting these alongside the score provides a record of the specific inference inputs.

## Decision Drivers

* Auditor explainability
* Feature traceability

## Considered Options

* Persist score with model and feature snapshot
* Persist score and model version only

## Decision Outcome

Chosen option: "Persist score with model and feature snapshot".

The required audit trail names both the model version and features, so storing a feature snapshot with each score most directly supports later review.

### Consequences

* Every score creates a durable record.
* Feature retention and access controls need definition.

## Pros and Cons of the Options

### Persist score with model and feature snapshot

* Good, because Direct audit evidence
* Good, because Reconstructs inference inputs
* Bad, because Storage and write overhead
* Bad, because Sensitive data retention

### Persist score and model version only

* Good, because Smaller records
* Good, because Fewer feature copies
* Bad, because Cannot inspect input values
* Bad, because Limited audit detail
