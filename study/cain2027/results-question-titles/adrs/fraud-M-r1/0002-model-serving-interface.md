# Model serving interface

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization system needs to request a score from an independently operated predictor. The brief does not specify a protocol, but the design space includes API-backed prediction services.

## Decision Drivers

* Authorization integration
* Low response time
* Service boundary

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST prediction service gives the authorization application a direct model API and has broader support in the design-space evidence than the gRPC option. “How to power up your product by machine learning with python microservice” and “Architecting a Machine Learning Pipeline” describe this integration pattern.

### Consequences

* The API contract becomes part of the authorization path.
* Measure request overhead against the latency budget.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Clear service boundary
* Good, because Common application integration
* Bad, because Serialization overhead
* Bad, because Requires API operations
* Sources: `s01_p05`, `s01_p08`, `s02_p10`, `s02_p11`, `s02_p12`

### gRPC model interface

* Good, because Independent model service
* Good, because Typed RPC interface
* Bad, because Requires client and server compatibility
* Bad, because Evidence covers few sources
* Sources: `s04_p01`
