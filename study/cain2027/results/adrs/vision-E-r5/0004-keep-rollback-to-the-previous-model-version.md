# Keep rollback to the previous model version

* System: On-device visual inspection

## Context and Problem Statement

Weekly model updates change the software running on production cameras. Retaining a known prior version gives the team a recovery path if an update performs poorly.

## Decision Drivers

* weekly updates
* production reliability

## Considered Options

* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Rollback supports recovery from a problematic weekly update; the model catalog must preserve the previous release for redeployment.

### Consequences

* Keep the prior model artifact available.
* Test rollback on the device fleet.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because recovery path
* Good, because limits impact of bad updates
* Bad, because retain prior model
* Bad, because rollback mechanism needed
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because simple active version
* Good, because less storage
* Bad, because no defined rollback path
* Sources: `d:10`, `v:10.3`
