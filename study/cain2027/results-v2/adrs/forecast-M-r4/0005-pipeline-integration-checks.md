# Pipeline integration checks

* System: Retail demand forecasting

## Context and Problem Statement

Model ideas can change data preparation, training, and evaluation components. Validating the full pipeline helps detect breaks before a candidate affects the weekly run.

## Decision Drivers

* Protect weekly run
* Fast model iteration

## Considered Options

* Automated full-pipeline integration testing (`v:14.1`)
* Training health validation (`v:14.5`)

## Decision Outcome

Chosen option: "Automated full-pipeline integration testing" (`v:14.1`).

Protecting the weekly run decides the choice: exercising the connected workflow can catch integration failures before promotion. The cost is additional compute and maintenance for test runs.

### Consequences

* Maintain representative test data and pipeline checks.
* Schedule validation so it does not compete with the weekly production run.

## Pros and Cons of the Options

### Automated full-pipeline integration testing

* Good, because Protect weekly run: exercises connected stages
* Good, because Fast iteration: repeatable validation
* Bad, because Compute cost: full pipeline runs consume resources
* Sources: `s01_p06`, `s02_p05`

### Training health validation

* Good, because Protect weekly run: detects unhealthy training
* Bad, because Coverage: does not validate all pipeline stages
* Sources: `s02_p11`
