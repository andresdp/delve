# Keep a previous model version available for rollback

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production without breaking the weekly run. The design space includes redeploying a previous model version as a rollback option (d:10).

## Decision Drivers

* Protect weekly run
* Fast model releases

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Retaining a prior model version gives the team a direct recovery path if a new release threatens the weekly forecast run (d:10, v:10.2).

### Consequences

* Retain deployable model artifacts and metadata.
* Document and periodically exercise rollback steps.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Provides recovery path
* Good, because Limits disruption from a bad release
* Bad, because Requires retained artifacts
* Bad, because Needs rollback procedure
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Enables concurrent versions
* Good, because Supports comparison
* Bad, because More production complexity
* Bad, because Requires traffic or output selection
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple active state
* Good, because Low operating overhead
* Bad, because No specified rollback path
* Bad, because Failed release can disrupt forecasts
* Sources: `d:10`, `v:10.3`
