# How should model versions be served?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify which model produced each score. Replacing models therefore needs to preserve a clear version boundary for serving and records.

## Decision Drivers

* Model version traceability
* Low latency
* Auditability

## Considered Options

* Versioned model artifacts loaded by scoring service
* Remote model service lookup per request

## Decision Outcome

Chosen option: "Versioned model artifacts loaded by scoring service".

Loading a specific versioned artifact keeps model identity explicit while avoiding a remote lookup on the latency-sensitive request path.

### Consequences

* Deployments must record the artifact version.
* Rollout and rollback need version controls.

## Pros and Cons of the Options

### Versioned model artifacts loaded by scoring service

* Good, because Explicit model identity
* Good, because Avoids per-request model lookup
* Bad, because Artifact rollout required

### Remote model service lookup per request

* Good, because Central model management
* Good, because Independent deployment
* Bad, because Network latency
* Bad, because Additional dependency
