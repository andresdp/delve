# Stage, validate, and retain prior model

*How should model updates be activated?*

* System: On-device visual inspection

## Context and Problem Statement

A newly retrained model is distributed to production devices, where a faulty or incompatible update could disrupt inspection. The brief does not specify a validation or recovery process.

## Decision Drivers

* production inspection
* weekly model changes
* small team

## Considered Options

* Replace model in place
* Stage, validate, and retain prior model

## Decision Outcome

Chosen option: "Stage, validate, and retain prior model".

Keeping the previous model available limits the impact of a failed update while allowing the weekly release cadence.

### Consequences

* Devices need storage for at least two model versions.
* Update software must validate packages and support rollback.

## Pros and Cons of the Options

### Replace model in place

* Good, because simple implementation
* Good, because low storage use
* Bad, because no quick rollback
* Bad, because interrupted update risk

### Stage, validate, and retain prior model

* Good, because rollback path
* Good, because checks before activation
* Bad, because extra device storage
* Bad, because more update logic
