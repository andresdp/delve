# How should model releases reach devices?

* System: On-device visual inspection

## Context and Problem Statement

Retrained models are pushed to production devices weekly, and an unsuccessful update could disrupt inspection. The design space includes staged releases that allow rollback.

## Decision Drivers

* Weekly update cadence
* Production continuity
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Commit-triggered staged release automation (`v:19.2`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Production continuity decides the choice: rollback limits the impact of a problematic model update. This gives up some simplicity because staged rollout and recovery paths require setup.

### Consequences

* Retain a prior model version for recovery.
* Define how staged rollout maps to camera groups.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Production continuity: supports rollback
* Good, because Small team: automates release steps
* Bad, because Small team: staged rollout adds setup work
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s25_p01`, `s25_p06`

### Commit-triggered staged release automation

* Good, because Small team: automates build and deployment
* Good, because Weekly cadence: repeatable release path
* Bad, because Production continuity: rollback is not explicit
