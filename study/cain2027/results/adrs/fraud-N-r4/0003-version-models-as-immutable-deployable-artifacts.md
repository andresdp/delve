# Version models as immutable deployable artifacts

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify which model produced each historical score.

## Decision Drivers

* Auditability
* Model attribution
* Online scoring

## Considered Options

* Immutable versioned model artifacts
* Replace a shared model in place

## Decision Outcome

Chosen option: "Immutable versioned model artifacts".

Immutable versions give each score a stable model identifier and make historical attribution and rollback practical.

### Consequences

* Retain artifacts for the audit period
* Record the deployed version with every score

## Pros and Cons of the Options

### Immutable versioned model artifacts

* Good, because Stable model identity
* Good, because Supports controlled rollout
* Bad, because Requires artifact retention
* Bad, because Deployment metadata needed

### Replace a shared model in place

* Good, because Simple update path
* Good, because Less artifact management
* Bad, because Historical identity is ambiguous
* Bad, because Rollback is harder
