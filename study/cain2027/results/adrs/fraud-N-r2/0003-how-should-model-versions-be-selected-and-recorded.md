# How should model versions be selected and recorded?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later identify which model version produced each score. Scoring and audit records therefore need a stable version association.

## Decision Drivers

* Auditable model version
* Low latency

## Considered Options

* Pin a version per scoring deployment
* Resolve a version on every request

## Decision Outcome

Chosen option: "Pin a version per scoring deployment".

A deployment-pinned version provides a clear version identifier for each score without adding per-request version resolution to the latency-sensitive path.

### Consequences

* Each score record must include the pinned version identifier.
* Rollouts must preserve the association between requests and versions.

## Pros and Cons of the Options

### Pin a version per scoring deployment

* Good, because Stable version per instance
* Good, because Fast local selection
* Bad, because Rollouts need coordination
* Bad, because Old versions need retention

### Resolve a version on every request

* Good, because Central version control
* Good, because Flexible routing
* Bad, because Adds runtime dependency
* Bad, because Selection can vary per request
