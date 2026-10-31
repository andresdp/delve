# Prediction service performance testing

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring path has a tens-of-milliseconds target and must remain available during peaks. Its latency and capacity need direct validation.

## Decision Drivers

* Latency target
* Peak load
* Online availability

## Considered Options

* Prediction service performance testing (`v:26.13`)
* System integration testing (`v:26.5`)
* Canary testing (`v:26.1`)

## Decision Outcome

Chosen option: "Prediction service performance testing" (`v:26.13`).

This directly tests the service whose response time constrains authorization and whose capacity must hold during peaks. Canary testing remains a useful deployment practice, but performance testing is the direct fit for this decision.

### Consequences

* Set latency and peak-load acceptance thresholds.
* Repeat performance checks for serving changes.

## Pros and Cons of the Options

### Prediction service performance testing

* Good, because Tests service performance
* Good, because Targets latency behavior
* Bad, because Needs representative load
* Bad, because Requires repeatable test setup
* Sources: `d:26`, `v:26.13`

### System integration testing

* Good, because Checks system interactions
* Good, because Finds integration failures
* Bad, because May not test peak capacity
* Bad, because Latency coverage varies
* Sources: `d:26`, `v:26.5`

### Canary testing

* Good, because Limits release exposure
* Good, because Tests in production conditions
* Bad, because Requires traffic controls
* Bad, because Does not replace load testing
* Sources: `d:26`, `v:26.1`
