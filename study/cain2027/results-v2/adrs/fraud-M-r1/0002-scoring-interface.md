# Scoring interface

* System: Card-fraud scoring service

## Context and Problem Statement

The payment authorization flow needs a request-response interface to obtain a fraud score. The brief does not specify a protocol.

## Decision Drivers

* Latency: tens of milliseconds
* Availability: peaks

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

The brief prioritizes latency but sets no protocol constraint; REST is supported across more practitioner sources and fits the online service choice. I accept possible protocol overhead and would need to validate it against the tens-of-milliseconds target. “Three Levels of ML Software” and “Architecting a Machine Learning System for Risk” discuss REST prediction services.

### Consequences

* Integrate authorization through a prediction API.
* Measure end-to-end request latency, including feature access.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Availability: API service can be independently deployed
* Bad, because Latency: request and serialization overhead
* Sources: `s01_p05`, `s02_p10`, `s10_p03`, `s19_p08`

### gRPC model interface

* Good, because Latency: compact service-to-service interface
* Bad, because Availability: requires compatible client integration
* Sources: `s19_p14`, `s21_p10`
