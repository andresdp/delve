# Model release strategy

* System: On-device visual inspection

## Context and Problem Statement

Newly trained models must reach cameras that may be offline. A bad update could disrupt defect detection until a device reconnects.

## Decision Drivers

* Reliable inference
* Weekly rollout
* Small-team operations

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Reliable inference decides the choice: progressive rollout with rollback limits the impact of a faulty update, at the cost of release setup. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support progressive releases and rollback.

### Consequences

* Devices need a way to receive updates incrementally.
* The previous model version must remain available for rollback.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Reliable inference: enables incremental rollout and rollback
* Bad, because Small-team operations: rollout process needs setup
* Sources: `s04_p10`, `s25_p09`

### Unified release automation

* Good, because Weekly rollout: automates build and release
* Bad, because Reliable inference: rollback is not explicit
* Sources: `s19_p05`, `s20_p05`
