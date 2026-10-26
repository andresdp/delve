# Model version deployment

* System: Card-fraud scoring service

## Context and Problem Statement

The system must retain which model version produced each score and remain available during peaks. The design space includes single-version deployment, concurrent versions, and rollback (d:10).

## Decision Drivers

* Auditability
* Peak availability

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Peak availability decides: rollback provides a recovery path, while accepting that switching versions takes redeployment. The checked combination had no warnings, but the design space lists no sources attesting it.

### Consequences

* Record the active model version with each score.
* Keep the prior deployable model available for rollback.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Peak availability: allows recovery to prior version
* Good, because Auditability: previous version can be identified
* Bad, because Peak availability: switch requires redeployment
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Peak availability: supports concurrent versions
* Bad, because Auditability: score-to-version routing must be recorded
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Auditability: one active version to identify
* Bad, because Peak availability: no concurrent version during transition
* Sources: `d:10`, `v:10.3`
