# How should deployed model versions be managed?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need the model version for each score, while a faulty release must not interrupt scoring.

## Decision Drivers

* Auditability
* Peak availability

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Peak availability decides: rollback provides a direct recovery path from a faulty release. We give up concurrent model comparison and must record the exact version used per score for auditability.

### Consequences

* Store the model version with each score record.
* Keep prior deployable artifacts available for rollback.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Peak availability: restore a prior version
* Bad, because Auditability: requires recording which version scored each transaction
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Auditability: versions can coexist for comparison
* Bad, because Peak availability: added routing and capacity complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Peak availability: simpler serving setup
* Bad, because Auditability: limited release comparison
* Sources: `d:10`, `v:10.3`
