# Deploy model versions

* System: Card-fraud scoring service

## Context and Problem Statement

Each score must be attributable to a model version, while keeping the scoring service available through peaks. The design space lists concurrent versions, rollback, and a single production model (d:10).

## Decision Drivers

* Audit traceability
* Peak-load availability

## Considered Options

* N versions in production (`v:10.1`)
* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "N versions in production" (`v:10.1`).

Audit traceability decides in favor of keeping versions identifiable in production; the cost is additional serving capacity for concurrent versions.

### Consequences

* Tag every score with the model version used.
* Capacity planning must account for concurrently deployed models.

## Pros and Cons of the Options

### N versions in production

* Good, because Audit traceability: version is explicit per score
* Bad, because Peak-load availability: concurrent versions consume capacity
* Sources: `d:10`, `v:10.1`

### Rollback to previous model version

* Good, because Peak-load availability: provides a recovery path
* Bad, because Audit traceability: rollback alone does not capture the version used per score
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Peak-load availability: concentrates serving capacity
* Bad, because Audit traceability: requires separate version records
* Sources: `d:10`, `v:10.3`
