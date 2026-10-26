# Rollback to previous model version

*How should deployed model versions be handled?*

* System: On-device visual inspection

## Context and Problem Statement

New weekly models are pushed to production devices, so a faulty update needs a recovery path.

## Decision Drivers

* Weekly updates
* Production reliability
* On-device deployment

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Rollback provides a recovery path for weekly device updates without requiring multiple active versions.

### Consequences

* Devices or the delivery process must retain and restore a previous model.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Recovery from a bad update
* Good, because Uses a prior known version
* Bad, because Requires retaining prior model
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Multiple versions can coexist
* Bad, because More deployment complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active model state
* Bad, because No explicit fallback strategy
* Sources: `d:10`, `v:10.3`
