# Keep one model version in production and retain rollback

* System: Retail demand forecasting

## Context and Problem Statement

A new model must not break the weekly run. The design space covers single or multiple live versions and rollback to a prior version.

## Decision Drivers

* Protect weekly run
* Fast model changes

## Considered Options

* Single model in production (`v:10.3`)
* N versions in production (`v:10.1`)
* Rollback to previous model version (`v:10.2`)

## Decision Outcome

Chosen option: "Single model in production" (`v:10.3`).

A single production model keeps the weekly run straightforward; retain prior artifacts and a rollback procedure as an operational safeguard. The rival checked point also produced no warnings, and neither combination had source attestations.

### Consequences

* Promote a candidate only after checks pass.
* Keep the previous deployable model available for recovery.

## Pros and Cons of the Options

### Single model in production

* Good, because Simple production state
* Bad, because No concurrent live comparison
* Sources: `d:10`, `v:10.3`

### N versions in production

* Good, because Enables concurrent comparison
* Bad, because More routing and monitoring
* Sources: `d:10`, `v:10.1`

### Rollback to previous model version

* Good, because Recovery path for regressions
* Bad, because Requires retained deployable versions
* Sources: `d:10`, `v:10.2`
