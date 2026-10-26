# How should updated models be released?

* System: On-device visual inspection

## Context and Problem Statement

Selected models must reach cameras that may be disconnected, and a faulty update could impair production inspection.

## Decision Drivers

* Offline devices
* Frequent updates
* Production continuity

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Recovery-oriented release automation with manual intervention (`v:19.4`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Progressive release with rollback limits the impact of a problematic candidate while allowing updates to be staged across devices. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” document progressive release and rollback (s04_p10, s25_p06).

### Consequences

* Track deployed model versions per device.
* Provide a rollback path for failed updates.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental rollout
* Good, because Supports rollback
* Bad, because Requires rollout coordination
* Sources: `s04_p02`, `s04_p10`, `s25_p06`

### Recovery-oriented release automation with manual intervention

* Good, because Supports recovery
* Good, because Allows manual intervention
* Bad, because Manual recovery effort
* Sources: `s21_p02`, `s21_p09`, `s22_p03`
