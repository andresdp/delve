# Test prediction service performance

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring path has a tens-of-milliseconds target and must continue during peaks. The design space includes prediction-service performance testing (d:26).

## Decision Drivers

* Tens-of-milliseconds latency
* Peak-load availability

## Considered Options

* Prediction service performance testing (`v:26.13`)
* System integration testing (`v:26.5`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Prediction service performance testing" (`v:26.13`).

The latency target decides in favor of performance testing; it costs representative test capacity and still needs realistic peak traffic to assess availability.

### Consequences

* Measure latency under expected and peak load.
* Test results depend on representative traffic and environment.

## Pros and Cons of the Options

### Prediction service performance testing

* Good, because Latency: checks service response time
* Bad, because Peak-load availability: representative peak traffic must be modeled
* Sources: `d:26`, `v:26.13`

### System integration testing

* Good, because Peak-load availability: checks component interactions
* Bad, because Latency: may not establish a response-time bound
* Sources: `d:26`, `v:26.5`

### No testing

* Bad, because Latency: no evidence of response time
* Sources: `d:26`, `v:26.14`
