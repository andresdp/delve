# Expose predictions through a REST microservice

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization system needs a synchronous interface to request a fraud score and receive it within its latency budget.

## Decision Drivers

* Synchronous scoring
* Application integration

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A prediction service provides the authorization application a direct request-response interface. “How to power up your product by machine learning with python microservice, pt. 1” and “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” document API-backed prediction services.

### Consequences

* The API contract becomes part of the authorization integration.
* Network and service time consume the scoring budget.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Clear service boundary
* Good, because Widely integrated API
* Bad, because Network hop adds latency
* Sources: `s01_p05`, `s02_p10`, `s02_p11`

### gRPC model interface

* Good, because Independent service interface
* Bad, because Fewer sources support it
* Sources: `s19_p14`
