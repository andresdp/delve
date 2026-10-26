# REST prediction microservice

*What interface should the payment application use?*

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization path needs a direct request-response contract with the scoring capability. The design space supports both REST and gRPC interfaces.

## Decision Drivers

* Latency: tens of milliseconds
* Availability: authorization path

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

Latency requires synchronous scoring and both service interfaces can provide it; REST is selected as the API-backed microservice option represented by broader practitioner evidence. The extra network hop remains part of the latency budget.

### Consequences

* The payment application must handle scoring-service timeouts.
* The service contract must remain compatible with callers.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Availability: independent service boundary
* Good, because Latency: direct request-response scoring
* Bad, because Latency: network hop adds overhead
* Bad, because Availability: caller depends on service health
* Sources: `s01_p05`, `s02_p10`, `s02_p11`

### gRPC model interface

* Good, because Latency: direct service calls
* Good, because Availability: independent deployment
* Bad, because Latency: network hop adds overhead
* Bad, because Availability: caller depends on service health
