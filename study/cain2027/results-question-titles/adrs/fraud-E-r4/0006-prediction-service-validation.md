# Prediction service validation

* System: Card-fraud scoring service

## Context and Problem Statement

The score is on the authorization path and must meet a tight response time at peak load. Failures or slowdowns could delay transaction authorization.

## Decision Drivers

* Latency target
* Peak load

## Considered Options

* Prediction service performance testing (`v:26.13`)
* Prediction service API testing (`v:26.12`)
* System integration testing (`v:26.5`)

## Decision Outcome

Chosen option: "Prediction service performance testing" (`v:26.13`).

Choose performance testing because the brief sets a response-time constraint and peak availability requirement; API and integration checks remain useful complementary coverage. (d:26, v:26.13)

### Consequences

* Use representative transaction and peak-load profiles.
* Retest latency when model or feature access changes.

## Pros and Cons of the Options

### Prediction service performance testing

* Good, because Checks response time
* Good, because Can exercise load
* Bad, because Needs realistic workloads
* Bad, because Does not prove production behavior
* Sources: `d:26`, `v:26.13`

### Prediction service API testing

* Good, because Checks request contract
* Good, because Catches API failures
* Bad, because Does not measure peak latency
* Bad, because Needs separate load coverage
* Sources: `d:26`, `v:26.12`

### System integration testing

* Good, because Checks connected components
* Bad, because May miss peak bottlenecks
* Bad, because Broader test setup
* Sources: `d:26`, `v:26.5`
