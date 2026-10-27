# Keep a rollback path for deployed model updates

* System: On-device visual inspection

## Context and Problem Statement

Weekly updates reach production devices, where connectivity may be intermittent. A faulty model needs a recovery path that does not depend on immediate retraining.

## Decision Drivers

* Weekly updates
* Offline devices
* Release recovery

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Retaining a previous model gives the team a direct recovery option after a weekly update, while avoiding the added production complexity of running multiple versions (d:10, v:10.2).

### Consequences

* Retain and identify the prior model artifact.
* Provide a rollback mechanism for devices.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Known recovery target
* Good, because Supports recovery from a bad update
* Bad, because Requires retaining prior artifact
* Bad, because Device rollout state needs tracking
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Multiple versions available
* Good, because Can compare versions in production
* Bad, because More device storage
* Bad, because More rollout complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active state
* Good, because Lower storage needs
* Bad, because No explicit prior version choice
* Bad, because Recovery may take longer
* Sources: `d:10`, `v:10.3`
