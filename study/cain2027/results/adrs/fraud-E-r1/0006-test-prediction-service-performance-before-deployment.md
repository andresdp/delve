# Test prediction service performance before deployment

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring service must meet a tens-of-milliseconds budget and continue working during peaks.

## Decision Drivers

* Latency target
* Peak traffic
* Scoring availability

## Considered Options

* Prediction service performance testing (`v:26.13`)
* Prediction service API testing (`v:26.12`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Prediction service performance testing" (`v:26.13`).

Performance testing directly addresses the stated response-time and peak-load constraints; API testing alone does not establish either (d:26, v:26.13, v:26.12).

### Consequences

* Tests need workloads representative of peak traffic.
* Passing tests does not guarantee production capacity.

## Pros and Cons of the Options

### Prediction service performance testing

* Good, because Checks service performance
* Bad, because Requires representative test loads
* Sources: `d:26`, `v:26.13`

### Prediction service API testing

* Good, because Checks service API
* Bad, because Does not establish peak performance
* Sources: `d:26`, `v:26.12`

### No testing

* Bad, because Latency and peak behavior remain unchecked
* Sources: `d:26`, `v:26.14`
