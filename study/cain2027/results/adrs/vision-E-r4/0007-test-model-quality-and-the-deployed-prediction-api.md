# Test model quality and the deployed prediction API

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining and device deployment create recurring opportunities for regressions. The brief provides no explicit testing requirements, but these choices address trained models and prediction services in the design space.

## Decision Drivers

* Weekly releases
* Defect detection
* Device deployment

## Considered Options

* Testing trained model quality (`v:26.9`)
* Prediction service API testing (`v:26.12`)
* Canary testing (`v:26.1`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Quality checks on each trained model directly support the weekly release cycle; API testing and canary rollout remain complementary options (d:26, v:26.9).

### Consequences

* The team must define acceptance criteria for model quality.
* This choice does not specify a full device rollout test strategy.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Checks model output quality
* Bad, because Requires quality criteria
* Sources: `d:26`, `v:26.9`

### Prediction service API testing

* Good, because Checks serving interface
* Bad, because Does not measure model quality
* Sources: `d:26`, `v:26.12`

### Canary testing

* Good, because Exercises a limited rollout
* Bad, because Rollout coordination needed
* Sources: `d:26`, `v:26.1`
