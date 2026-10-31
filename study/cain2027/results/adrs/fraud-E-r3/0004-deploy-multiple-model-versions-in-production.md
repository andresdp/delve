# Deploy multiple model versions in production

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires later identification of the model version behind every score. Operating multiple versions makes version selection and score attribution explicit.

## Decision Drivers

* Model version audit
* Safe model changes
* Online service

## Considered Options

* N versions in production (`v:10.1`)
* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "N versions in production" (`v:10.1`).

Concurrent versions support staged change while preserving the ability to identify the version used for each score. This checked choice had no warnings, but the point was unattested; the design space also lists rollback as a separate alternative rather than a bundled choice.

### Consequences

* Attach the selected model version to every score record.
* Define routing and retirement rules for deployed versions.

## Pros and Cons of the Options

### N versions in production

* Good, because Supports concurrent versions
* Good, because Enables staged rollout
* Bad, because Routing complexity
* Bad, because More versions to track
* Sources: `d:10`, `v:10.1`

### Rollback to previous model version

* Good, because Recovery path
* Good, because Simple active version
* Bad, because Rollback procedure needed
* Bad, because Does not define rollout
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Simple routing
* Good, because One active version
* Bad, because No concurrent comparison
* Bad, because Replacement risk
* Sources: `d:10`, `v:10.3`
