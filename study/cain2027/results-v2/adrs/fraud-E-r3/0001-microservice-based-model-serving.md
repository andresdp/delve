# Microservice based model serving

*How should transaction scores be served?*

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a score before authorization, within tens of milliseconds, including during peaks.

## Decision Drivers

* Score latency
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Peak availability decides: an independently scalable service can absorb demand surges. We accept the network hop and must keep its latency within the score budget.

### Consequences

* Scale scoring capacity separately from payments application.
* Protect the synchronous call path with capacity limits and timeouts.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Peak availability: scale service independently
* Bad, because Score latency: network hop adds delay
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Score latency: local request path
* Bad, because Peak availability: shares application capacity
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Peak availability: process scheduled workloads
* Bad, because Score latency: not suitable before authorization
* Sources: `d:5`, `v:5.3`
