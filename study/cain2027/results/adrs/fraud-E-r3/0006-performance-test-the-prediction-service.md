# Performance test the prediction service

* System: Card-fraud scoring service

## Context and Problem Statement

The service must return scores within tens of milliseconds and continue working during peaks. Those runtime expectations need validation before release.

## Decision Drivers

* Response latency
* Peak capacity
* Release confidence

## Considered Options

* Prediction service performance testing (`v:26.13`)
* Prediction service API testing (`v:26.12`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Prediction service performance testing" (`v:26.13`).

Performance testing directly addresses the latency and peak-load drivers. The final design point had no warnings, though no sources attested to the complete combination.

### Consequences

* Define representative peak traffic and latency thresholds.
* Run performance checks before deployment.

## Pros and Cons of the Options

### Prediction service performance testing

* Good, because Tests service performance
* Good, because Relevant to latency targets
* Bad, because Test workload unspecified
* Bad, because Does not define pass thresholds
* Sources: `d:26`, `v:26.13`

### Prediction service API testing

* Good, because Checks request interface
* Good, because Catches API regressions
* Bad, because Does not establish capacity
* Bad, because Does not establish latency
* Sources: `d:26`, `v:26.12`

### No testing

* Good, because No test setup
* Good, because No test execution cost
* Bad, because Latency unverified
* Bad, because Peak behavior unknown
* Sources: `d:26`, `v:26.14`
