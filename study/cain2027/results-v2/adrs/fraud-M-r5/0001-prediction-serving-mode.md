# Prediction serving mode

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores are needed before each transaction is authorized, so predictions must be computed in the request path. Precomputing scores would risk using stale results.

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Queue-fronted online serving cluster (`v:31.1`)
* Precomputed offline serving (`v:31.6`)

## Decision Outcome

Chosen option: "Queue-fronted online serving cluster" (`v:31.1`).

Latency decides the choice: scoring must use the current transaction, so online serving is required. This gives up the lower request-path cost of batch computation and adds queue operations.

### Consequences

* Keep serving replicas available for peak traffic.
* Operate the queue and serving cluster as critical-path components.

## Pros and Cons of the Options

### Queue-fronted online serving cluster

* Good, because Low latency: distributes online predictors
* Good, because Peak availability: queue supports load balancing
* Bad, because Low latency: queue adds a request hop
* Bad, because Peak availability: cluster needs capacity management
* Sources: `s02_p11`, `s12_p07`, `s19_p15`

### Precomputed offline serving

* Good, because Peak availability: results are ready to read
* Good, because Cost: scores can be computed in batches
* Bad, because Low latency: misses current transaction context
* Bad, because Peak availability: stale results may be unusable
* Sources: `s12_p02`, `s12_p03`, `s19_p08`
