# Expose fraud scores through a REST prediction microservice

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs a synchronous scoring interface that returns within tens of milliseconds. The serving interface dimension requires a choice before runtime communication strategy.

## Decision Drivers

* Tens-of-milliseconds response
* Authorization integration

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

Choose the API-backed prediction service for direct authorization integration. Sources including “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” support this pattern; the checked design point and its gRPC rival were both unattested, with no warnings.

### Consequences

* Keep inference on the synchronous request path.
* Measure end-to-end latency against the actual budget.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Application-facing API
* Good, because Broad practitioner support
* Bad, because Latency budget needs validation
* Sources: `s01_p05`, `s02_p10`

### gRPC model interface

* Good, because Independent model service
* Bad, because Less evidence in this space
* Sources: `s19_p14`, `s21_p10`
