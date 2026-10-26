# What to test in the scoring pipeline?

* System: Card-fraud scoring service

## Context and Problem Statement

A latency miss can delay authorization, so the online prediction path needs explicit performance validation. The design space includes service performance testing and no testing (d:26).

## Decision Drivers

* latency bound
* peak load

## Considered Options

* Prediction service performance testing (`v:26.13`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Prediction service performance testing" (`v:26.13`).

Performance tests directly check the scoring path against the tens-of-milliseconds requirement and peak conditions (d:26).

### Consequences

* Test end-to-end requests at expected peak load.
* Gate releases on latency targets.

## Pros and Cons of the Options

### Prediction service performance testing

* Good, because Checks latency
* Good, because Exercises service capacity
* Bad, because Needs representative load
* Bad, because Adds release work
* Sources: `d:26`, `v:26.13`

### No testing

* Good, because No test setup
* Good, because Fast releases
* Bad, because Latency regressions unseen
* Bad, because Capacity unknown
* Sources: `d:26`, `v:26.14`
