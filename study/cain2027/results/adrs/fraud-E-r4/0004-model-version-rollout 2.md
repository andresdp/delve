# Model version rollout

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need the model version associated with every score. Rollout and rollback should preserve the ability to identify which version handled a transaction.

## Decision Drivers

* Version audit trail
* Safe recovery

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Choose rollback to a prior version to provide a recovery path while logging the active model version for each score. The local design point had no warnings but no attesting sources; this is a novel, unchecked-in-practice combination in this design space. (d:10, v:10.2)

### Consequences

* Retain deployable model artifacts and version metadata.
* Log model version with every score.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Known recovery path
* Good, because Limits faulty version exposure
* Bad, because Requires retained artifact
* Bad, because Rollback coordination
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Supports parallel versions
* Good, because Enables staged rollout
* Bad, because Routing complexity
* Bad, because More versions to track
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple routing
* Good, because One active version
* Bad, because No parallel rollout
* Bad, because Replacement risk
* Sources: `d:10`, `v:10.3`
