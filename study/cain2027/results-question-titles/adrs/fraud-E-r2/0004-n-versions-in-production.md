# N versions in production

*How many model versions should run in production?*

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires later identification of the model version used for each score, while the service must remain available during peaks.

## Decision Drivers

* Version traceability
* Service availability

## Considered Options

* N versions in production (`v:10.1`)
* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "N versions in production" (`v:10.1`).

The design space supports running multiple versions concurrently, and production tracking can associate each score with its model version (d:10, v:10.1; d:22, v:22.4). The checked combination had no warnings but was unattested; the rival was also warning-free and unattested.

### Consequences

* Include the serving model version in each score record.
* Define how versions are selected and retired.

## Pros and Cons of the Options

### N versions in production

* Good, because Multiple versions can run
* Good, because Supports version-specific scoring
* Bad, because More versions to track
* Sources: `d:10`, `v:10.1`

### Rollback to previous model version

* Good, because Previous version can be restored
* Bad, because Rollback procedure needed
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because One active version to track
* Bad, because No concurrent version option
* Sources: `d:10`, `v:10.3`
