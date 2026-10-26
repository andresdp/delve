# How should model updates reach devices?

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must be pushed to devices, where an update can affect production inspection. Release automation offers staged rollout and rollback options.

## Decision Drivers

* Safe weekly updates
* Production continuity
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Environment-gated deployment automation (`v:19.3`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Production continuity decides the choice: staged rollout with rollback limits the impact of a bad model update. This gives up the simpler release flow of environment gates alone and adds coordination across device versions; Productionizing Machine Learning with a Microservices Architecture and Azure Machine Learning describe this approach.

### Consequences

* Track which model version each device is running.
* Provide a tested path to restore a prior model version.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Production continuity: supports staged updates and rollback
* Good, because Small team: automates repeatable release steps
* Bad, because Production continuity: staged rollout adds release complexity
* Bad, because Small team: rollback requires version and device coordination
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`

### Environment-gated deployment automation

* Good, because Production continuity: validation gates precede production
* Good, because Small team: automates environment-specific release steps
* Bad, because Safe weekly updates: no explicit rollback capability
* Bad, because Production continuity: gates can slow a weekly release
