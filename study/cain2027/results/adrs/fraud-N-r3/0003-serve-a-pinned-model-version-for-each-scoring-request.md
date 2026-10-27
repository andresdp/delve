# Serve a pinned model version for each scoring request

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to identify the model version that produced each score. Recording the version with the score makes the inference result traceable across model updates.

## Decision Drivers

* Audit traceability
* Low-latency inference

## Considered Options

* Pinned model artifact per worker
* Fetch a model for every request

## Decision Outcome

Chosen option: "Pinned model artifact per worker".

Keeping a known artifact available to each worker avoids a per-request model fetch and lets the service attach an explicit version to every result.

### Consequences

* Rollouts must manage model versions across workers.
* Model artifacts need versioned identifiers.

## Pros and Cons of the Options

### Pinned model artifact per worker

* Good, because Predictable inference
* Good, because Explicit version identity
* Bad, because Rollouts require coordination
* Bad, because Workers may hold stale versions

### Fetch a model for every request

* Good, because Central version control
* Good, because Updates take effect quickly
* Bad, because Adds request latency
* Bad, because Model source becomes a dependency
