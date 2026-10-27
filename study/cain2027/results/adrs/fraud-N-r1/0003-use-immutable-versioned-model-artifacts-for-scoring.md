# Use immutable, versioned model artifacts for scoring

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify which model produced each transaction score.

## Decision Drivers

* Model version traceability
* Auditability

## Considered Options

* Immutable, versioned model artifacts
* Replace the active model in place

## Decision Outcome

Chosen option: "Immutable, versioned model artifacts".

Recording a stable model version with each score makes the model used for that decision identifiable later.

### Consequences

* Each score must retain its model version identifier.

## Pros and Cons of the Options

### Immutable, versioned model artifacts

* Good, because Identifies the scoring model
* Good, because Supports historical reconstruction
* Bad, because Requires version management
* Bad, because Retains older artifacts

### Replace the active model in place

* Good, because Simple deployment process
* Good, because Uses little artifact storage
* Bad, because Obscures past model versions
* Bad, because Weakens audit reconstruction
