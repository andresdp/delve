# Keep a rollback path for deployed models

* System: On-device visual inspection

## Context and Problem Statement

Weekly releases change the model running on production cameras. A way to restore a prior version limits the impact of a faulty release.

## Decision Drivers

* Weekly releases
* Production inspection

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

The design space describes this option as redeploying the prior version and switching back to it (d:10, v:10.2).

### Consequences

* Retain the previous deployable model artifact.
* Device rollout must support switching versions.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Restores prior model
* Good, because Supports recovery
* Bad, because Previous artifact must be retained
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Multiple versions available
* Bad, because More deployment complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active deployment
* Bad, because No explicit version fallback
* Sources: `d:10`, `v:10.3`
