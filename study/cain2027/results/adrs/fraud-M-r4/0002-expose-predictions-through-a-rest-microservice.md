# Expose predictions through a REST microservice

* System: Card-fraud scoring service

## Context and Problem Statement

The payment authorization path needs a request-response interface to obtain a transaction score from an independently operated model.

## Decision Drivers

* Online scoring
* Application integration
* Low latency

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST prediction microservice provides a clear application integration boundary, while the brief does not require a particular transport optimization. Sources describe REST-backed model prediction services (How to power up your product by machine learning with python microservice, pt. 1; Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2).

### Consequences

* Keep request and response schemas versioned.
* Measure end-to-end latency, including feature lookup and network time.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because API-backed integration
* Good, because Broad practitioner support
* Bad, because Network hop adds latency
* Sources: `s01_p05`, `s02_p10`, `s02_p11`

### gRPC model interface

* Good, because Independent service interface
* Bad, because Fewer sources in this design space
* Sources: `s19_p14`, `s21_p10`
