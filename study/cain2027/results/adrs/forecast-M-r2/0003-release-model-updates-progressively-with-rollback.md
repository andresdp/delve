# Release model updates progressively with rollback

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a fast route to production without putting the weekly run at risk.

## Decision Drivers

* Safe weekly run
* Fast production changes
* Recovery

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Commit-triggered staged release automation (`v:19.2`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Progressive rollout and the ability to revert directly address the requirement to introduce model ideas without disrupting the weekly run. Productionizing Machine Learning with a Microservices Architecture and Azure Machine Learning document incremental release and recovery practices.

### Consequences

* Keep the prior model version deployable.
* Define rollout and rollback criteria.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental rollout
* Good, because Can restore prior version
* Bad, because Requires release automation
* Bad, because Needs rollback readiness
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s25_p06`

### Commit-triggered staged release automation

* Good, because Automates build and promotion
* Good, because Speeds routine releases
* Bad, because Does not itself specify rollback
* Bad, because Requires staged environments
* Sources: `s06_p02`, `s06_p06`, `s06_p13`
