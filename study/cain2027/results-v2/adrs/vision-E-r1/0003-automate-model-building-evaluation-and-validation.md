# Automate model building, evaluation and validation

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining needs a repeatable path from labeled images to a candidate model. The design space includes an automated model-building pipeline and development-tool training (d:18).

## Decision Drivers

* Weekly retraining
* Small team and tight budget

## Considered Options

* Model building pipeline (`v:18.1`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Model building pipeline" (`v:18.1`).

Weekly retraining decides the choice: an automated pipeline makes the weekly process repeatable. The team takes on initial setup and maintenance.

### Consequences

* Represent training, evaluation and validation as pipeline steps.
* Keep pipeline operation proportionate to the small team.

## Pros and Cons of the Options

### Model building pipeline

* Good, because Weekly retraining: repeatable automated runs
* Bad, because Small team: pipeline setup and upkeep
* Sources: `d:18`, `v:18.1`

### Model building in development tool

* Good, because Small team: simple initial workflow
* Bad, because Weekly retraining: manual repeat work
* Sources: `d:18`, `v:18.3`
