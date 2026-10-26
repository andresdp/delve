# Model building pipeline

*How should models be built and validated?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a path to production that does not destabilize the established weekly run.

## Decision Drivers

* Fast iteration
* Repeatable model evaluation
* Protect weekly run

## Considered Options

* Model building pipeline (`v:18.1`)
* Model builder component (`v:18.2`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Model building pipeline" (`v:18.1`).

An automated training, evaluation, and validation pipeline makes model changes repeatable before delivery; the checked combination had no warnings and no attested sources.

### Consequences

* Training and evaluation steps become maintained pipeline code.
* A model must pass validation before production delivery.

## Pros and Cons of the Options

### Model building pipeline

* Good, because Automates training and validation
* Good, because Repeatable execution
* Bad, because Requires pipeline upkeep
* Sources: `d:18`, `v:18.1`

### Model builder component

* Good, because Dedicated building component
* Bad, because Requires component integration
* Sources: `d:18`, `v:18.2`

### Model building in development tool

* Good, because Quick experimentation
* Bad, because Less repeatable production path
* Sources: `d:18`, `v:18.3`
