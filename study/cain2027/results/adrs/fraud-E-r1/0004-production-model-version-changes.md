# Production model version changes

* System: Card-fraud scoring service

## Context and Problem Statement

Scores must be attributable to a specific model version, and an unsuitable release must be reversible without interrupting scoring.

## Decision Drivers

* Auditable model version
* Continuous scoring
* Recovery from bad release

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Rollback provides a direct recovery option while keeping a single active scoring version. Logging the selected version on every score preserves the audit trail across releases.

### Consequences

* Retain the previous deployable model artifact.
* Record active model version with each score.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Known recovery path
* Good, because Restores prior version
* Bad, because Rollback needs coordination
* Bad, because Previous version must remain available
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Multiple versions available
* Good, because Supports staged release
* Bad, because More routing complexity
* Bad, because Requires version attribution
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple routing
* Good, because One active version
* Bad, because Limited release flexibility
* Bad, because Recovery preparation needed
* Sources: `d:10`, `v:10.3`
