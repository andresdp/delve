# Serving interface

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization flow needs to request a score from a deployed model and receive it promptly.

## Decision Drivers

* Low-latency request response
* Payments application integration
* Model version traceability

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

Choose an API-backed prediction service to integrate scoring with the payments application. “Architecting a Machine Learning System for Risk” and “Architecting a Machine Learning Pipeline” provide supporting examples; the brief does not specify protocol constraints.

### Consequences

* The authorization path depends on service availability.
* Request and response schemas need governance.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Application-facing API
* Good, because Independent serving component
* Bad, because Network call adds latency
* Bad, because Requires service operations
* Sources: `s01_p05`, `s02_p10`, `s10_p03`

### gRPC model interface

* Good, because Independent model service
* Good, because Typed service contract
* Bad, because Requires client compatibility
* Bad, because No brief-specific evidence
