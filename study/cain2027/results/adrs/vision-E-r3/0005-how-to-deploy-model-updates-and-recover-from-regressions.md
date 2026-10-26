# How to deploy model updates and recover from regressions?

* System: On-device visual inspection

## Context and Problem Statement

Retraining produces a new model each week, and the model must reach production devices. A poor update could disrupt line inspection.

## Decision Drivers

* Weekly model updates
* Production inspection
* Offline devices

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Keeping a prior model available gives the team a recovery option for weekly updates. The design point has no warnings, but no attesting sources.

### Consequences

* Retain the previous model on devices or an update source.
* Define how devices switch back after a failed update.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Provides a recovery path
* Bad, because Requires retaining prior model
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Supports parallel model versions
* Bad, because Adds rollout complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active model state
* Bad, because No explicit rollback strategy
* Sources: `d:10`, `v:10.3`
