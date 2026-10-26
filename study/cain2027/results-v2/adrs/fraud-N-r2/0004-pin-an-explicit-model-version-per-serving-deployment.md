# Pin an explicit model version per serving deployment

*How should model versions be selected for scoring?*

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to know which model produced each score. Explicit version selection and recording make that association clear across model updates.

## Decision Drivers

* Auditability
* Low latency

## Considered Options

* Pin an explicit model version per serving deployment
* Resolve the active model version on every request

## Decision Outcome

Chosen option: "Pin an explicit model version per serving deployment".

Auditability favors a stable, recorded version, and avoiding a per-request lookup also serves latency; this gives up the simplicity of centrally switching versions.

### Consequences

* Include model version in each score record.
* Coordinate model updates with serving deployments.

## Pros and Cons of the Options

### Pin an explicit model version per serving deployment

* Good, because Auditability: stable version identity per deployment
* Bad, because Peak availability: rollout requires coordinated deployment

### Resolve the active model version on every request

* Good, because Peak availability: model changes can take effect centrally
* Bad, because Low latency: adds per-request lookup work
