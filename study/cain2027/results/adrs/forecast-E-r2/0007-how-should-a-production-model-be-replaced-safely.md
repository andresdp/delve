# How should a production model be replaced safely?

* System: Retail demand forecasting

## Context and Problem Statement

New models need to reach production without breaking the recurring forecast run. Keeping a rollback path supports recovery if a release causes problems. [d:10, v:10.2]

## Decision Drivers

* Safe model releases
* Weekly run continuity

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

A rollback option provides a direct recovery path if a new model disrupts forecasting, supporting continuity of the weekly run. [d:10, v:10.2]

### Consequences

* Keep the prior model version deployable.
* Define how a failed release is detected and reversed.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Recovery path after release
* Good, because Limits disruption
* Bad, because Previous version must remain available
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Multiple versions can coexist
* Bad, because Adds version management
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active model setup
* Bad, because No explicit rollback mechanism
* Sources: `d:10`, `v:10.3`
