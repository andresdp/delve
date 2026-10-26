# How should production model versions be managed?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production without breaking the established weekly run. Keeping a known previous version available supports recovery.

## Decision Drivers

* Protect weekly run
* Model iteration
* Recoverability

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Retaining and redeploying the previous model provides a recovery path when a new model affects the weekly forecast run (d:10, v:10.2).

### Consequences

* Model artifacts and metadata need retention.
* Promotion and rollback need a defined procedure.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Clear recovery path
* Good, because Supports controlled promotion
* Bad, because Requires version retention
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Parallel comparison
* Bad, because More operational complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active state
* Bad, because Rollback not inherent
* Sources: `d:10`, `v:10.3`
