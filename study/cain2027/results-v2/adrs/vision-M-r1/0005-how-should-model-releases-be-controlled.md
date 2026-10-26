# How should model releases be controlled?

* System: On-device visual inspection

## Context and Problem Statement

A retrained model must reach devices that may be offline, so a failed release should not leave the production line without a usable model. The design space offers progressive release with rollback and unified release automation.

## Decision Drivers

* Offline operation
* Safe weekly updates
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Safe weekly updates decide the choice: incremental rollout with rollback limits the impact of a bad model, at the cost of tracking release state across devices. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support this approach.

### Consequences

* Retain the previous known-good model on each device.
* Track which devices have received each model version.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Safe weekly updates: incremental rollout and rollback
* Bad, because Small team: rollout tracking adds operational work
* Sources: `s04_p10`, `s25_p06`

### Unified release automation

* Good, because Small team: one automated build and release process
* Bad, because Safe weekly updates: rollback behavior is not explicit
* Sources: `s19_p05`, `s20_p05`
