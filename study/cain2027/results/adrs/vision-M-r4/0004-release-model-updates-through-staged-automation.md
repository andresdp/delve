# Release model updates through staged automation

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must be pushed to devices, and the small team has limited capacity for manual release work. Releases need a repeatable path from model build to deployment.

## Decision Drivers

* Weekly model updates
* Small team
* Device deployment

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Staged automation gives a repeatable path to build, validate, and promote each weekly model artifact. Sources Google’s *MLOps: Continuous delivery and automation pipelines in machine learning*, *Continuous Intelligence: Moving Machine Learning Application into Production Reliably*, and *Architectural thinking in the Wild West of data science* describe this approach (s06_p02, s08_p01, s13_p09).

### Consequences

* Model artifacts need a controlled promotion path.
* The pipeline must account for devices that are temporarily offline.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because Automates build and promotion
* Good, because Supports delivery stages
* Bad, because Requires release pipeline setup
* Bad, because Pipeline must support device rollout
* Sources: `s06_p02`, `s06_p13`, `s08_p01`

### Unified release automation

* Good, because One process for model and service
* Good, because Automates build and release
* Bad, because May couple model and service releases
* Bad, because Less explicit stage detail
* Sources: `s02_p11`, `s19_p05`, `s20_p02`
