# Keep model versions identifiable and selectable

* System: Card-fraud scoring service

## Context and Problem Statement

Audit records need to refer to the exact model version used, and the live service must be able to use a model to score transactions.

## Decision Drivers

* Model version traceability
* Live scoring

## Considered Options

* Versioned model artifacts with explicit serving selection
* Replace a single mutable model artifact

## Decision Outcome

Chosen option: "Versioned model artifacts with explicit serving selection".

Versioned artifacts let each score record refer to an identifiable model while the service selects the version it serves.

### Consequences

* Artifact versions must remain available for audit needs.
* Model rollout and rollback require operational controls.

## Pros and Cons of the Options

### Versioned model artifacts with explicit serving selection

* Good, because Stable version references
* Good, because Controlled model selection
* Bad, because Requires artifact and rollout management

### Replace a single mutable model artifact

* Good, because Simple artifact handling
* Good, because Few deployment controls
* Bad, because Version history can be lost
* Bad, because Audits may not identify the model
