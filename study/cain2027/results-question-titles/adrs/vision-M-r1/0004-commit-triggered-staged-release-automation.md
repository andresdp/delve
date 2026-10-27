# Commit-triggered staged release automation

*How should model releases reach devices?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining creates frequent model artifacts that must be pushed to devices, including those that may be offline during a rollout.

## Decision Drivers

* weekly model updates
* intermittent connectivity
* safe rollout

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Staged promotion supports automated build and validation before distribution. The architecture must account for devices receiving the promoted model only when connectivity returns.

### Consequences

* Validate and package each model before promotion.
* Retain the last known good model on devices.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because repeatable builds
* Good, because staged promotion
* Bad, because pipeline setup
* Bad, because device delivery still needed
* Sources: `s06_p02`, `s06_p13`, `s08_p01`

### Unified release automation

* Good, because one release process
* Good, because automated packaging
* Bad, because less explicit staging
* Bad, because rollback not specified
