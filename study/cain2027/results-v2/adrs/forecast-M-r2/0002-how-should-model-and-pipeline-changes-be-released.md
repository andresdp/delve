# How should model and pipeline changes be released?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production quickly without jeopardizing the weekly forecast run. Releases need a way to validate changes and restore a prior version if a production update causes trouble.

## Decision Drivers

* Weekly-run reliability
* Fast model iteration
* Past-week reproducibility

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Environment-gated deployment automation (`v:19.3`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Weekly-run reliability decides the choice: progressive rollout and rollback limit the impact of a bad update. This gives up some simplicity because release automation and rollback paths require maintenance; sources include “Productionizing Machine Learning with a Microservices Architecture” and Azure’s “MLOps: Model management, deployment, and monitoring with Azure Machine Learning.”

### Consequences

* Keep the prior production model available for rollback.
* Validate updates before full production use.
* Maintain release and recovery automation.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Reliability: incremental rollout and rollback
* Good, because Fast iteration: automated promotion path
* Bad, because Team effort: release automation upkeep
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s25_p06`

### Environment-gated deployment automation

* Good, because Reliability: stronger checks before production
* Bad, because Fast iteration: approval gates add delay
* Sources: `s09_p11`, `s10_p07`
