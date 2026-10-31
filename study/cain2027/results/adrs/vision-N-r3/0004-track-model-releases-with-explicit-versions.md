# Track model releases with explicit versions

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining creates successive model artifacts that must be distributed to devices. Explicit versions make it possible to identify which model each device is using.

## Decision Drivers

* Weekly retraining
* Device rollout

## Considered Options

* Versioned model releases
* Replace a single latest model file

## Decision Outcome

Chosen option: "Versioned model releases".

Versioned releases let the team distinguish weekly artifacts and identify the model installed on each device.

### Consequences

* Each release needs a stable identifier.
* The system needs a retention policy for older artifacts.

## Pros and Cons of the Options

### Versioned model releases

* Good, because Traceable deployments
* Good, because Supports rollback
* Bad, because Release bookkeeping
* Bad, because Version policy needed

### Replace a single latest model file

* Good, because Simple storage
* Good, because Few release steps
* Bad, because Weak deployment traceability
* Bad, because Rollback is harder
