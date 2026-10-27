# Release automation

* System: Retail demand forecasting

## Context and Problem Statement

Model and pipeline changes need a controlled path to production without endangering the recurring forecast. Staged automation can apply checks before promotion.

## Decision Drivers

* Protect weekly run
* Fast releases
* Recoverability

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Commit-triggered builds and staged promotion fit the desire to deliver ideas quickly while applying checks before production. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” support this pattern. The checked point has no warnings but is unattested.

### Consequences

* Maintain separate validation and production stages.
* A failed gate blocks promotion until resolved.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because Automates build and checks
* Good, because Stages promotion
* Bad, because CI upkeep
* Bad, because Requires release discipline
* Sources: `s06_p02`, `s06_p06`, `s06_p13`, `s06_p14`, `s06_p15`, `s08_p01`, `s08_p02`, `s13_p09`

### Unified release automation

* Good, because One release process
* Good, because Builds and packages together
* Bad, because Less explicit staging
* Bad, because Rollback not specified
