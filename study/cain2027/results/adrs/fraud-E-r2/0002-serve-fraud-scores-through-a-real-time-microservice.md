# Serve fraud scores through a real-time microservice

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs each transaction’s score before it can proceed. Scheduled batch scoring cannot meet that timing requirement.

## Decision Drivers

* Tens-of-milliseconds response
* Continuous peaks

## Considered Options

* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Real-time service scoring matches the authorization flow; batch serving returns results too late. The brief does not specify a particular scaling mechanism for peak demand.

### Consequences

* Scale capacity for transaction peaks.
* Keep the synchronous scoring path within the latency budget.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time scoring
* Good, because Independent scaling
* Bad, because Network overhead
* Bad, because Service availability dependency
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because Scheduled processing
* Good, because Batch efficiency
* Bad, because Delayed results
* Bad, because Cannot gate authorization
* Sources: `d:5`, `v:5.3`
