# Use progressive releases with rollback for model updates

* System: On-device visual inspection

## Context and Problem Statement

Weekly retrained models must reach devices reliably, with a recovery path if a new model causes problems.

## Decision Drivers

* Weekly model pushes
* Safe recovery
* Limited operations capacity

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Progressive rollout and rollback reduce the risk of distributing a faulty weekly model. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support this approach.

### Consequences

* Keep a prior model version available for restoration.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental rollout
* Good, because Rollback support
* Bad, because Release coordination effort
* Sources: `s04_p03`, `s25_p06`

### Unified release automation

* Good, because One release process
* Good, because Automates packaging
* Bad, because Rollback not specified
* Sources: `s02_p11`, `s19_p05`
