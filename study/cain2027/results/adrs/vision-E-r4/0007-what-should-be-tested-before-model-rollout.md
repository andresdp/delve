# What should be tested before model rollout?

* System: On-device visual inspection

## Context and Problem Statement

Retrained models are distributed to production cameras. A quality gate helps prevent an unacceptable model from reaching devices.

## Decision Drivers

* Defect detection quality
* Weekly rollout
* Production reliability

## Considered Options

* Testing trained model quality (`v:26.9`)
* Canary testing (`v:26.1`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Checking trained model quality fits the retraining workflow and provides a gate before deployment to the production line (d:26, v:26.9).

### Consequences

* The team needs a representative evaluation set.
* The quality threshold must be defined.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Quality gate for models
* Good, because Catches regressions
* Bad, because Needs labeled evaluation data
* Sources: `d:26`, `v:26.9`

### Canary testing

* Good, because Limits initial exposure
* Bad, because Requires staged rollout support
* Sources: `d:26`, `v:26.1`
