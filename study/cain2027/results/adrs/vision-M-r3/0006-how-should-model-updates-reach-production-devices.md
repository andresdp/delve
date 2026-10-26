# How should model updates reach production devices?

* System: On-device visual inspection

## Context and Problem Statement

Models are pushed to devices, so releases must account for distributed deployment and recovery if a candidate causes problems. The brief does not describe device connectivity or rollout controls.

## Decision Drivers

* Device updates
* Production continuity

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Choose staged rollout with rollback as the safer release pattern for a distributed device fleet. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support progressive releases; device-specific delivery remains outside the design space evidence.

### Consequences

* Keep a prior model available for recovery.
* Define how devices receive updates when connectivity returns.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental rollout
* Good, because Supports rollback
* Bad, because Requires rollout coordination
* Bad, because May be difficult across offline devices
* Sources: `s04_p02`, `s04_p10`, `s25_p01`, `s25_p06`

### Unified release automation

* Good, because One automated release process
* Good, because Builds and packages together
* Bad, because Less explicit staged rollout
* Bad, because Rollback is not specified
* Sources: `s06_p07`, `s25_p09`
