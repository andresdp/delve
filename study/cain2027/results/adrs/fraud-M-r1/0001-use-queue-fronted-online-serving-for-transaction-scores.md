# Use queue-fronted online serving for transaction scores

* System: Card-fraud scoring service

## Context and Problem Statement

Scores must be returned during authorization in tens of milliseconds, including at peak load.

## Decision Drivers

* Low latency
* Peak availability

## Considered Options

* Queue-fronted online serving cluster (`v:31.1`)
* Precomputed offline serving (`v:31.6`)

## Decision Outcome

Chosen option: "Queue-fronted online serving cluster" (`v:31.1`).

A distributed online scoring cluster behind a queue fits synchronous scoring and peak traffic. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” describes this pattern for load balancing, throughput, and low latency.

### Consequences

* Queueing and serving capacity need operational management.
* The authorization path depends on the serving cluster.

## Pros and Cons of the Options

### Queue-fronted online serving cluster

* Good, because Balances peak load
* Good, because Supports low latency
* Bad, because Adds queue operations
* Sources: `s02_p11`, `s02_p13`, `s12_p07`

### Precomputed offline serving

* Good, because Decouples scoring from request path
* Bad, because Can be stale
* Bad, because Cannot use current context
* Sources: `s12_p02`
