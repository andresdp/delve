# Progressive release automation with rollback

*How should model releases protect the weekly run?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a route to production that does not jeopardize the established weekly forecast. A release should be reversible if it causes problems.

## Decision Drivers

* Weekly run safety
* Fast model iteration
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Weekly run safety decides: progressive promotion with rollback limits the impact of a faulty model release. This adds release process upkeep; “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” describe staged deployment and restoration.

### Consequences

* Previous production versions must remain available.
* Promotion stages need clear validation and rollback criteria.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Weekly run safety: enables rollback after a bad release
* Good, because Fast iteration: automates staged promotion
* Bad, because Small team: release stages and rollback need upkeep
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`

### Unified release automation

* Good, because Fast iteration: automates build and release
* Bad, because Weekly run safety: rollback is not explicit
* Sources: ``
