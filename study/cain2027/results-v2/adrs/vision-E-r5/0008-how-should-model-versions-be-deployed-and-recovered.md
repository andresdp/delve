# How should model versions be deployed and recovered?

* System: On-device visual inspection

## Context and Problem Statement

Weekly device updates can introduce regressions, so deployment needs a recovery path.

## Decision Drivers

* Offline operation
* Weekly updates
* Reproducibility

## Considered Options

* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Offline operation decides the choice: retaining a prior model allows recovery without depending on network access. This gives up device storage for previous artifacts. The design space has no source passages; this choice is grounded in d:10 and v:10.2.

### Consequences

* Devices retain a known prior model.
* Deployment tracks current and previous versions.
* Rollback policy must define when to switch.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Offline operation: previous artifact can remain on device
* Good, because Weekly updates: supports recovery after a bad release
* Bad, because Tight budget: retains prior model artifacts
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Tight budget: stores only the current model
* Bad, because Weekly updates: recovery path is unspecified
* Bad, because Offline operation: remote recovery may be unavailable
* Sources: `d:10`, `v:10.3`
