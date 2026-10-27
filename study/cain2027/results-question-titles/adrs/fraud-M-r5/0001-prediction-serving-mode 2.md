# Prediction serving mode

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores are needed before each authorization, so predictions must use current transaction context within tens of milliseconds.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Online computation serving (`v:31.5`)
* Queue-fronted online serving cluster (`v:31.1`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Online computation serving" (`v:31.5`).

Choose request-time scoring because the decision must use transaction context before authorization. Sources including “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” support online computation; the batch alternative does not meet this request-time need.

### Consequences

* Feature retrieval must fit the latency budget.
* Capacity must handle peak request volume.

## Pros and Cons of the Options

### Online computation serving

* Good, because Uses current request context
* Good, because Supports timely scoring
* Bad, because Depends on fast feature retrieval
* Bad, because Latency budget is tight
* Sources: `s02_p02`, `s02_p13`, `s04_p10`

### Queue-fronted online serving cluster

* Good, because Balances serving load
* Good, because Supports throughput and low latency
* Bad, because Adds queue operations
* Bad, because Queue delay affects response time
* Sources: `s02_p11`, `s02_p13`, `s12_p07`

### Scheduled batch prediction deployment

* Good, because Scores ahead of time
* Good, because Useful for bulk workloads
* Bad, because May use stale context
* Bad, because Does not fit authorization flow
