# Use commit-triggered staged release automation

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without disrupting the weekly run. Releases need repeatable validation and a controlled path into production.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Release consistency

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Choose repository-triggered builds and tests with staged promotion to speed delivery while providing checkpoints before production. “MLOps: Continuous delivery and automation pipelines in machine learning” describes commit-triggered releases across delivery stages.

### Consequences

* Release checks must finish before promotion.
* Staging environments and promotion rules require ownership.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because Automates build and tests
* Good, because Stages promotion
* Bad, because Pipeline upkeep
* Bad, because Requires release gates
* Sources: `s06_p02`, `s06_p06`, `s06_p13`, `s06_p14`, `s06_p15`, `s08_p01`, `s08_p02`

### Unified release automation

* Good, because One release process
* Good, because Automates packaging
* Bad, because Less explicit staging
* Bad, because Broader process scope
* Sources: `s02_p11`, `s19_p05`, `s20_p02`, `s20_p05`
