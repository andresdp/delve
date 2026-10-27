# Record model version and feature snapshot with each score

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later be able to identify which model version and features produced a score. Recording them alongside the result makes that provenance retrievable after model or feature changes.

## Decision Drivers

* Audit explainability
* Model version traceability
* Feature traceability

## Considered Options

* Persist score with model version and feature snapshot
* Persist score and model version only

## Decision Outcome

Chosen option: "Persist score with model version and feature snapshot".

The brief requires auditors to know both the model version and features used, so both must be captured with the score. Access controls and retention rules are needed for the stored feature data.

### Consequences

* Each decision creates an audit record
* Feature data needs access and retention controls

## Pros and Cons of the Options

### Persist score with model version and feature snapshot

* Good, because Direct decision reconstruction
* Good, because Auditable feature provenance
* Bad, because Storage and retention cost
* Bad, because Sensitive data handling

### Persist score and model version only

* Good, because Lower storage cost
* Good, because Simpler logging
* Bad, because Features cannot be verified
* Bad, because Limited decision reconstruction
