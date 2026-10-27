# ML release automation

* System: Retail demand forecasting

## Context and Problem Statement

The team wants new model ideas to reach production promptly while protecting the recurring weekly run.

## Decision Drivers

* Fast releases
* Safe weekly operation
* Small team

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Environment-gated deployment automation (`v:19.3`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Repository-triggered builds, tests, and staged promotion support fast iteration while providing repeatable checks before production. Support includes “MLOps: Continuous delivery and automation pipelines in machine learning” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably.”

### Consequences

* Changes must pass automated build and test stages.
* Release automation needs a maintained deployment path.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because Automated build and promotion
* Good, because Repeatable releases
* Bad, because Requires CI setup
* Bad, because Pipeline failures need ownership
* Sources: `s06_p06`, `s06_p13`, `s08_p01`

### Environment-gated deployment automation

* Good, because Validation before production
* Good, because Environment controls
* Bad, because Approval can slow release
* Bad, because More stages to manage
* Sources: `s09_p11`, `s10_p07`
