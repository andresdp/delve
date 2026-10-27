# Keep a rollback path for production models

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production without breaking the weekly forecast run. The design space includes rollback to a previous version and multiple or single versions in production (d:10).

## Decision Drivers

* Protect weekly run
* Fast model iteration

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Rollback gives the team a recovery option if a new model disrupts the weekly run (d:10, v:10.2).

### Consequences

* Retain deployable previous model versions.
* Provide a way to switch back after a faulty release.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Supports recovery
* Bad, because Requires prior version retention
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Allows concurrent versions
* Bad, because Adds production complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active model
* Bad, because No explicit rollback path
* Sources: `d:10`, `v:10.3`
