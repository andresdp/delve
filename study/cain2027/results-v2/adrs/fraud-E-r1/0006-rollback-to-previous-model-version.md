# Rollback to previous model version

*How to manage model versions in production?*

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need the model version for every score, and production must remain available while versions change (d:10).

## Decision Drivers

* Audit traceability
* Peak availability

## Considered Options

* Single model in production (`v:10.3`)
* N versions in production (`v:10.1`)
* Rollback to previous model version (`v:10.2`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Peak availability decides the choice: rollback provides a recovery path after a bad release; preserving the version-to-score history adds operational recordkeeping.

### Consequences

* Maintain a deployable previous model version.
* Record the active model version for each score.

## Pros and Cons of the Options

### Single model in production

* Good, because Audit traceability: one active version
* Bad, because Peak availability: rollout may require a switch
* Sources: `d:10`, `v:10.3`

### N versions in production

* Good, because Peak availability: versions can coexist
* Bad, because Audit traceability: route and record version per score
* Sources: `d:10`, `v:10.1`

### Rollback to previous model version

* Good, because Peak availability: restore prior version
* Bad, because Audit traceability: preserve version history
* Sources: `d:10`, `v:10.2`
