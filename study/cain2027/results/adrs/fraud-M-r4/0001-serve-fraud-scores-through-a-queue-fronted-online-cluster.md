# Serve fraud scores through a queue-fronted online cluster

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization requires a score within tens of milliseconds, including during transaction peaks.

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability
* Real-time authorization

## Considered Options

* Queue-fronted online serving cluster (`v:31.1`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Queue-fronted online serving cluster" (`v:31.1`).

The queue-fronted cluster distributes online predictors for throughput and low latency, which fits authorization-time scoring better than scheduled batch output (Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2; System Architectures for Personalization and Recommendation). The checked design point had no warnings, though no source attested to the full combination.

### Consequences

* Operate a queue and multiple predictors.
* Set capacity and overload behavior to meet the latency target.

## Pros and Cons of the Options

### Queue-fronted online serving cluster

* Good, because Load balances requests
* Good, because Targets low latency
* Bad, because Adds queue operations
* Sources: `s02_p11`, `s02_p13`, `s12_p07`

### Scheduled batch prediction deployment

* Good, because Efficient bulk scoring
* Good, because Writes results to storage
* Bad, because Scores may be stale
* Bad, because Cannot score each live transaction
* Sources: `s02_p02`, `s02_p12`
