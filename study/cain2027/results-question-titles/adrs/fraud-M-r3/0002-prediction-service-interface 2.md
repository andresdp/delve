# Prediction service interface

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization path needs a synchronous way to submit transaction features and receive a score. The brief does not specify an API protocol.

## Decision Drivers

* Synchronous scoring
* Application integration
* Low latency

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

Choose a REST prediction service as a clear application boundary; the brief provides no client or protocol constraints to justify a narrower choice.

### Consequences

* Define request, response, timeout, and error contracts.
* Measure end-to-end latency under peak load.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because API-backed integration
* Good, because Practitioner evidence
* Bad, because Protocol overhead must be measured
* Sources: `s01_p05`, `s02_p10`

### gRPC model interface

* Good, because Supports independent deployment
* Good, because Practitioner evidence
* Bad, because Protocol choice needs client compatibility
* Sources: `s19_p14`, `s21_p10`
