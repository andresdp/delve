# What production tests should gate model releases?

* System: Card-fraud scoring service

## Context and Problem Statement

A bad model or service release could affect transaction authorization. The brief gives latency and availability requirements, so rollout and performance checks matter.

## Decision Drivers

* low latency
* peak availability
* safe model updates

## Considered Options

* Canary testing (`v:26.1`)
* Prediction service performance testing (`v:26.13`)
* Testing trained model quality (`v:26.9`)

## Decision Outcome

Chosen option: "Canary testing" (`v:26.1`).

A canary limits exposure during rollout, while performance tests should also verify the latency and peak-load requirements. (d:26, v:26.1, v:26.13)

### Consequences

* Define release thresholds and rollback criteria.
* Measure service performance under peak load.

## Pros and Cons of the Options

### Canary testing

* Good, because limits initial exposure
* Good, because checks release in production
* Bad, because requires traffic control
* Bad, because needs rollback criteria
* Sources: `d:26`, `v:26.1`

### Prediction service performance testing

* Good, because checks response performance
* Good, because can exercise peak load
* Bad, because test environment may differ
* Bad, because does not assess model quality
* Sources: `d:26`, `v:26.13`

### Testing trained model quality

* Good, because checks predictive quality
* Good, because can gate model release
* Bad, because needs representative data
* Bad, because does not check serving capacity
* Sources: `d:26`, `v:26.9`
