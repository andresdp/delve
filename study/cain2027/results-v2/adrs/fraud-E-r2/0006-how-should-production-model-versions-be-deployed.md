# How should production model versions be deployed?

* System: Card-fraud scoring service

## Context and Problem Statement

Scores must remain available through peaks, and auditors need to associate each score with the model version that produced it. The design space distinguishes multiple concurrent versions, rollback, or a single production version (d:10).

## Decision Drivers

* Peak availability
* Audit traceability

## Considered Options

* N versions in production (`v:10.1`)
* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "N versions in production" (`v:10.1`).

Peak availability decides: concurrent versions permit staged rollout while maintaining production scoring. This costs more to operate and requires recording the version used for every score.

### Consequences

* Production must support routing to multiple model versions.
* Score records need the selected model version.

## Pros and Cons of the Options

### N versions in production

* Good, because Availability: allows staged or parallel deployment
* Good, because Traceability: versions can be identified per score
* Bad, because Cost: operate multiple versions concurrently
* Sources: `d:10`, `v:10.1`

### Rollback to previous model version

* Good, because Availability: return to a prior model after a bad release
* Bad, because Traceability: rollback does not itself identify version per score
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Cost: run one production model
* Bad, because Availability: release transition can be a risk
* Sources: `d:10`, `v:10.3`
