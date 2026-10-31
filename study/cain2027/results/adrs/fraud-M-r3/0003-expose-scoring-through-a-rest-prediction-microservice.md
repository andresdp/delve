# Expose scoring through a REST prediction microservice

* System: Card-fraud scoring service

## Context and Problem Statement

The payments authorization flow needs a request-response interface for fraud scores. A separate prediction endpoint provides a clear integration boundary.

## Decision Drivers

* Synchronous scoring
* Low latency
* Application integration

## Considered Options

* REST prediction microservice (`v:29.1`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST prediction endpoint matches the authorization request-response interaction and keeps model integration independent. Practitioner sources describe API-backed prediction services for application integration.

### Consequences

* Budget the API and feature lookup within the latency target.
* Version the request and response contract.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Direct request-response API
* Good, because Independent deployment
* Bad, because Network hop adds latency
* Sources: `s01_p05`, `s02_p10`

### PMML-based model serving

* Good, because Portable model format
* Good, because Supports online scoring
* Bad, because Requires compatible tooling
