# Microservice based model serving

*How to serve scores?*

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization flow needs a transaction score in real time, making online serving necessary (d:5).

## Decision Drivers

* Tens-of-ms latency
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Peak availability decides the choice: distributed serving can scale for transaction peaks; the cost is remote-call overhead against the latency target.

### Consequences

* Provision and scale serving capacity for peaks.
* Measure request latency across the network boundary.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Peak availability: distributed service
* Bad, because Latency: remote call overhead
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Latency: local call
* Bad, because Peak availability: shares local capacity
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Peak availability: scheduled workload
* Bad, because Latency: no immediate score
* Sources: `d:5`, `v:5.3`
