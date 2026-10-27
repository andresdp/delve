# Model release safety

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the scheduled weekly forecast. Releases need a way to limit impact and recover.

## Decision Drivers

* Protect weekly run
* Fast model delivery
* Recoverability

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Incremental promotion and rollback directly address the risk of a new model disrupting the weekly run. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support this release pattern.

### Consequences

* Keep a known-good model available for recovery.
* Add staged promotion to the release path.
* Automate rollback or document its operational trigger.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental production updates
* Good, because Can revert a bad release
* Bad, because Requires release automation
* Bad, because Adds promotion steps
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`

### Unified release automation

* Good, because Automates build and release
* Good, because One delivery process
* Bad, because Rollback not explicit
