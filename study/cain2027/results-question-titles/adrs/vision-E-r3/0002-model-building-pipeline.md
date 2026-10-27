# Model building pipeline

*How to structure model building?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining needs a repeatable path from images to an evaluated model. The team is small and has a tight infrastructure budget.

## Decision Drivers

* Repeatable retraining
* Small team
* Tight budget

## Considered Options

* Model building pipeline (`v:18.1`)
* Model builder component (`v:18.2`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Model building pipeline" (`v:18.1`).

A pipeline makes weekly training, evaluation, and validation repeatable. The design point has no warnings, but no attesting sources.

### Consequences

* Automate the recurring build steps.
* Maintain the pipeline as part of the system.

## Pros and Cons of the Options

### Model building pipeline

* Good, because Automates training and evaluation
* Good, because Repeatable runs
* Bad, because Requires pipeline setup
* Sources: `d:18`, `v:18.1`

### Model builder component

* Good, because Dedicated training component
* Bad, because Needs integration work
* Sources: `d:18`, `v:18.2`

### Model building in development tool

* Good, because Low initial setup
* Bad, because Less repeatable operation
* Sources: `d:18`, `v:18.3`
