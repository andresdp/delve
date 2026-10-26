# Testing trained model quality

*What should be tested before model release?*

* System: On-device visual inspection

## Context and Problem Statement

A newly trained model is pushed to production each week, making a quality gate important before deployment.

## Decision Drivers

* Reproducibility
* Weekly updates
* Tight budget

## Considered Options

* Testing trained model quality (`v:26.9`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Weekly updates decide the choice: test every trained model before it reaches devices. This gives up some compute and evaluation-data budget. The design space has no source passages; this choice is grounded in d:26 and v:26.9.

### Consequences

* Each release requires an evaluation set.
* Quality thresholds must be defined.
* Failed candidates need a release hold.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Reproducibility: applies a quality gate to each model
* Good, because Weekly updates: checks every trained release
* Bad, because Tight budget: requires labelled evaluation data and compute
* Sources: `d:26`, `v:26.9`

### No testing

* Good, because Tight budget: no test infrastructure
* Bad, because Weekly updates: defects can ship with each release
* Bad, because Reproducibility: no consistent quality gate
* Sources: `d:26`, `v:26.14`
