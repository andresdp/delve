# Release forecast updates progressively with rollback

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a quick route to production, but releases must not disrupt the weekly forecast run.

## Decision Drivers

* Fast model updates
* Weekly run continuity

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Recovery-oriented release automation with manual intervention (`v:19.4`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Incremental promotion and rollback limit the impact of a faulty model while keeping model updates automated. Productionizing Machine Learning with a Microservices Architecture and MLOps: Model management, deployment, and monitoring with Azure Machine Learning describe this approach.

### Consequences

* Maintain a known prior model for rollback.
* Release stages add operational steps.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental production updates
* Good, because Rollback path
* Bad, because Requires release stages
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`

### Recovery-oriented release automation with manual intervention

* Good, because Supports restoration
* Good, because Allows manual recovery
* Bad, because Manual recovery can slow release
* Sources: `s21_p02`, `s21_p03`, `s21_p09`, `s21_p10`, `s21_p11`, `s21_p18`, `s22_p01`, `s22_p03`, `s22_p15`
