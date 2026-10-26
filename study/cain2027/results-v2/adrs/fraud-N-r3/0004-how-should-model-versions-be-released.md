# How should model versions be released?

* System: Card-fraud scoring service

## Context and Problem Statement

Each score must be attributable to a model version, but the brief does not define release cadence, rollback needs, or model validation requirements.

## Decision Drivers

* Auditability
* Peak resilience

## Considered Options

* Deploy immutable, versioned model artifacts
* Update model files in place
* Select model version per transaction

## Decision Outcome

Chosen option: "Deploy immutable, versioned model artifacts".

Auditability decides the choice because immutable artifacts make the model identity for each score stable. This gives up the simplicity of in-place updates and requires coordinated rollout handling.

### Consequences

* Audit records can refer to fixed artifact identifiers.
* Rollbacks require retaining prior artifacts.

## Pros and Cons of the Options

### Deploy immutable, versioned model artifacts

* Good, because Auditability: stable model identity
* Bad, because Peak resilience: rollout must coordinate instances

### Update model files in place

* Good, because Peak resilience: simple deployment
* Bad, because Auditability: model identity can become ambiguous

### Select model version per transaction

* Good, because Auditability: records explicit version choice
* Bad, because Low latency: adds selection work
