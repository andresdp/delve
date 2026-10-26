# Queue-fronted online serving cluster

*How should transaction scores be served?*

* System: Card-fraud scoring service

## Context and Problem Statement

Each authorization request needs a fresh fraud score within tens of milliseconds, including at peak load.

## Decision Drivers

* Latency: tens of milliseconds
* Availability: peak traffic

## Considered Options

* Queue-fronted online serving cluster (`v:31.1`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Queue-fronted online serving cluster" (`v:31.1`).

Transaction-path latency decides the choice: online scoring can use the current request, while queueing and replication support peaks. This gives up the efficiency of batch scoring and adds serving infrastructure.

### Consequences

* Keep serving capacity available for peak traffic.
* Queueing and feature retrieval consume part of the latency budget.

## Pros and Cons of the Options

### Queue-fronted online serving cluster

* Good, because Latency: online predictors score current requests
* Good, because Availability: queue distributes peak load
* Bad, because Availability: queue adds a dependency
* Bad, because Cost: distributed cluster needs capacity
* Sources: `s02_p11`, `s02_p13`, `s12_p07`

### Scheduled batch prediction deployment

* Good, because Cost: scores can be computed in batches
* Good, because Availability: precomputed results can be served
* Bad, because Latency: misses new transaction context
* Bad, because Latency: stale scores may delay decisions
* Sources: `s02_p02`, `s02_p12`, `s02_p13`
