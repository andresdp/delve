# Prediction serving

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a score before authorization proceeds, so predictions must be available online. Serving capacity must handle peaks.

## Decision Drivers

* Synchronous scoring
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Choose real-time microservice serving to scale scoring independently during peaks; verify the network path meets the tens-of-milliseconds constraint. (d:5, v:5.1)

### Consequences

* Provide capacity headroom and service health checks.
* Keep request and model loading overhead within the latency budget.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time scoring
* Good, because Independent scaling
* Bad, because Network overhead
* Bad, because Service operations
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Local request path
* Good, because Fewer remote dependencies
* Bad, because Tighter coupling
* Bad, because Scaling tied to host
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Efficient bulk scoring
* Bad, because Not request-time
* Bad, because Stale score risk
* Sources: `d:5`, `v:5.3`
