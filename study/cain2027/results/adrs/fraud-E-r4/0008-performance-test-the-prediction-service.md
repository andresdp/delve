# Performance test the prediction service

* System: Card-fraud scoring service

## Context and Problem Statement

The score must return within tens of milliseconds and the service must continue working during peaks. The workspace includes prediction service performance testing as a testing alternative. (d:26)

## Decision Drivers

* Tens of milliseconds
* Peak traffic

## Considered Options

* Prediction service performance testing (`v:26.13`)
* System integration testing (`v:26.5`)

## Decision Outcome

Chosen option: "Prediction service performance testing" (`v:26.13`).

Performance testing directly addresses both latency and peak operation. The rival point selected integration testing and returned no warnings, but does not directly test the stated response-time driver. (d:26, v:26.13)

### Consequences

* Define latency and peak load acceptance thresholds.
* Run performance checks against the deployed scoring path.

## Pros and Cons of the Options

### Prediction service performance testing

* Good, because Targets service response time
* Good, because Can exercise peak load
* Bad, because Needs representative load profiles
* Bad, because Testing adds release work
* Sources: `d:26`, `v:26.13`

### System integration testing

* Good, because Checks component interactions
* Good, because Finds integration failures
* Bad, because Does not establish latency limits
* Bad, because May not represent peak load
* Sources: `d:26`, `v:26.5`
