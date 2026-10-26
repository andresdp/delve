# Prediction serving interface

* System: Card-fraud scoring service

## Context and Problem Statement

Each card transaction needs a synchronous fraud score before authorization. The brief does not specify an API protocol.

## Decision Drivers

* Tens-of-milliseconds scoring
* Peak availability

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

Tens-of-milliseconds scoring decides in favor of a direct request and response interface. This accepts a network hop; the design space does not establish that REST meets a specific latency target.

### Consequences

* The authorization path depends on the prediction service.
* Measure end-to-end latency under peak load.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Low latency: direct prediction request
* Good, because Availability: independently exposed service
* Bad, because Latency: network hop per request
* Sources: `s01_p05`, `s02_p10`

### gRPC model interface

* Good, because Low latency: compact service interface
* Bad, because Availability: separate service dependency

### PMML-based model serving

* Good, because Availability: portable model representation
* Bad, because Latency: compatible runtime required
