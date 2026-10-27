# Keep a rollback path for deployed model versions

* System: On-device visual inspection

## Context and Problem Statement

A new model is pushed to cameras that may be offline. The deployment choice should allow recovery when a release causes problems.

## Decision Drivers

* Device deployments
* Offline operation
* Weekly updates

## Considered Options

* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Keeping the prior model available gives operators a recovery option if a pushed version performs poorly (d:10, v:10.2).

### Consequences

* Store the previous package on devices or in the distribution channel.
* Define how offline cameras receive rollback instructions.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Recovery path
* Good, because Supports staged device updates
* Bad, because Retain prior artifact
* Bad, because Rollback procedure needed
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Simple active state
* Bad, because No explicit prior-version path
* Sources: `d:10`, `v:10.3`
