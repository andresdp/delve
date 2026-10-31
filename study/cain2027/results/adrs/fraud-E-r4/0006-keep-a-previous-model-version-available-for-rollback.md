# Keep a previous model version available for rollback

* System: Card-fraud scoring service

## Context and Problem Statement

A scoring service must remain usable during peaks, and auditors need the serving model version tied to each score. A rollback path limits the impact of a problematic release. (d:10)

## Decision Drivers

* Peak availability
* Model version traceability

## Considered Options

* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)
* N versions in production (`v:10.1`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Retaining a known prior version gives operators a recovery option while preserving explicit version identity. The checked point returned no warnings, though it was unattested. (d:10, v:10.2)

### Consequences

* Each score needs the active model version recorded.
* Release procedures must support switching back.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Recovery path for bad releases
* Good, because Clear version switch
* Bad, because Previous artifact must be retained
* Bad, because Rollback needs operational procedure
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Simple serving state
* Good, because One active version
* Bad, because No explicit rollback path
* Bad, because Release failures affect scoring
* Sources: `d:10`, `v:10.3`

### N versions in production

* Good, because Multiple versions available
* Good, because Supports parallel deployment
* Bad, because More complex score attribution
* Bad, because Higher serving resource use
* Sources: `d:10`, `v:10.1`
