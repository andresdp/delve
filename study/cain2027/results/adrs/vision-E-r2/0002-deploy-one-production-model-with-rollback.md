# Deploy one production model with rollback

* System: On-device visual inspection

## Context and Problem Statement

Each device needs a clear active model, while weekly updates create a need to recover from a bad release.

## Decision Drivers

* Device deployment
* Weekly updates
* Operational simplicity

## Considered Options

* Single model in production (`v:10.3`)
* N versions in production (`v:10.1`)
* Rollback to previous model version (`v:10.2`)

## Decision Outcome

Chosen option: "Single model in production" (`v:10.3`).

A single active model keeps device operation simple; retain and redeploy the previous artifact as a recovery procedure (d:10, v:10.3, v:10.2).

### Consequences

* Keep the prior model available for rollback.
* Model comparison requires a separate process.

## Pros and Cons of the Options

### Single model in production

* Good, because Simple active version
* Good, because Low device overhead
* Bad, because No parallel comparison
* Sources: `d:10`, `v:10.3`

### N versions in production

* Good, because Supports comparison
* Good, because Gradual rollout
* Bad, because More device storage
* Bad, because More deployment complexity
* Sources: `d:10`, `v:10.1`

### Rollback to previous model version

* Good, because Recovery path
* Good, because Limits release impact
* Bad, because Retain prior artifact
* Bad, because Rollback coordination
* Sources: `d:10`, `v:10.2`
