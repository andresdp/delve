# Keep rollback available and track deployed models

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production without disrupting the weekly run, so releases need a recovery path and production tracking. The design space includes rollback and tracking choices (d:10, d:22).

## Decision Drivers

* Protect weekly run
* Reversible releases
* Operational visibility

## Considered Options

* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)
* Model in-production tracking (`v:22.4`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Rollback gives the team a direct response when a new model threatens the weekly run. Pair it with model in-production tracking (d:22, v:22.4) to record usage, inputs, and outputs; these are separate dimensions in the checked point.

### Consequences

* Retain the previous deployable model version.
* Record model identity and run inputs alongside forecasts.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Provides recovery path
* Good, because Limits impact of a poor release
* Bad, because Requires retaining prior model
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Simple active deployment
* Bad, because Needs explicit rollback procedure
* Sources: `d:10`, `v:10.3`

### Model in-production tracking

* Good, because Tracks model inputs and outputs
* Good, because Improves production visibility
* Bad, because Adds tracking and retention work
* Sources: `d:22`, `v:22.4`

### No in-production monitoring

* Good, because Least operational setup
* Bad, because Limited visibility into failures
* Sources: `d:22`, `v:22.3`
