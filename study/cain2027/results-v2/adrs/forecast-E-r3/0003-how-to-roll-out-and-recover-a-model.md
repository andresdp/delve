# How to roll out and recover a model

* System: Retail demand forecasting

## Context and Problem Statement

A new model must reach production without disrupting the weekly forecast. The design space considers rollback, multiple production versions, and a single production model (d:10).

## Decision Drivers

* Protect weekly run
* Production speed

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Protecting the weekly run decides the choice: make recovery to a known model version part of deployment, at the cost of a rollback step. The design point returned no warnings; its rival using a single production model also returned no warnings, and neither had attesting sources.

### Consequences

* Keep the previous model version available for recovery.
* Include rollback in the release procedure.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Protect weekly run: permits recovery
* Bad, because Production speed: rollback needs a release step
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Production speed: supports concurrent versions
* Bad, because Protect weekly run: increases operational complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Protect weekly run: simpler production state
* Bad, because Production speed: less room for gradual rollout
* Sources: `d:10`, `v:10.3`
