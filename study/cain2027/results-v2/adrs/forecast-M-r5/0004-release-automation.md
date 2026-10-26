# Release automation

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly, but a bad release must not disrupt the weekly forecast run.

## Decision Drivers

* Protect weekly run
* Fast production changes

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Commit-triggered staged release automation (`v:19.2`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Protecting the weekly run decides: progressive rollout with rollback contains release problems, though staging adds steps. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support rollback; the checked point has no warnings but is unattested as a complete combination.

### Consequences

* Keep a known-good model available for restoration.
* Production promotion takes additional stages.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Weekly run: incremental rollout and rollback
* Bad, because Fast production changes: staged promotion adds steps
* Sources: `s04_p03`, `s04_p10`, `s25_p06`

### Commit-triggered staged release automation

* Good, because Fast production changes: commits start delivery
* Bad, because Weekly run: requires effective validation gates
* Sources: `s06_p02`, `s06_p13`
