# Commit-triggered staged release automation

*How should code and model changes reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly forecast run. Release automation can validate changes before promotion.

## Decision Drivers

* fast model iteration
* protect weekly run
* small team

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Recovery-oriented release automation with manual intervention (`v:19.4`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Automated builds, tests, and staged promotion let the team iterate while guarding the weekly run. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” support this release path.

### Consequences

* Gate production promotion on validation.
* Keep the prior production model available for recovery.
* Maintain automated build and release workflows.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because automated validation
* Good, because staged promotion
* Bad, because pipeline setup effort
* Bad, because release failures need recovery
* Sources: `s06_p02`, `s06_p13`, `s08_p01`

### Recovery-oriented release automation with manual intervention

* Good, because supports rollback
* Good, because allows operator recovery
* Bad, because manual recovery load
* Bad, because slower routine promotion
* Sources: `s06_p13`, `s08_p02`
