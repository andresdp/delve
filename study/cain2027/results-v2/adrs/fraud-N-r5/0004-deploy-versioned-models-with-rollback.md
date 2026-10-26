# Deploy versioned models with rollback

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need the model version used for each score, so model identity must be explicit across deployments. The brief does not specify a release strategy.

## Decision Drivers

* Auditor traceability
* Peak availability

## Considered Options

* Versioned model artifacts with staged rollout and rollback
* Replace the active model in place
* Run a fixed model until a service release

## Decision Outcome

Chosen option: "Versioned model artifacts with staged rollout and rollback".

Auditor traceability decides the choice: immutable model versions make each score’s model identity clear. Staged rollout adds release work, and the scoring path must handle version transitions safely.

### Consequences

* Attach an immutable model version to every score record.
* Retain prior artifacts for rollback and audit needs.
* Coordinate staged rollout with serving capacity.

## Pros and Cons of the Options

### Versioned model artifacts with staged rollout and rollback

* Good, because Auditor traceability: immutable versions identify scoring behavior
* Good, because Peak availability: rollback restores a known serving version
* Bad, because Peak availability: staged rollout adds operational steps

### Replace the active model in place

* Good, because Peak availability: simple deployment flow
* Bad, because Auditor traceability: model identity can be ambiguous
* Bad, because Peak availability: rollback may require rebuilding the prior state

### Run a fixed model until a service release

* Good, because Peak availability: model and service change together
* Bad, because Auditor traceability: version history needs release-level tracking
* Bad, because Peak availability: model updates depend on service rollout
