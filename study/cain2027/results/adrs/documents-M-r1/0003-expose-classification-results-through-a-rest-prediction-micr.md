# Expose classification results through a REST prediction microservice

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classification results, so the system needs a common integration boundary. The brief does not specify a required client protocol.

## Decision Drivers

* Multiple consumers
* Shared integration boundary
* Operational reuse

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST interface gives consuming teams a shared integration point; pair it with persisted batch results for scheduled scoring. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Three Levels of ML Software” describe API-backed prediction services.

### Consequences

* Specify a stable request and result schema.
* Coordinate service access and version changes across teams.
* Clarify whether consumers read stored results or submit requests.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Common API boundary
* Good, because Supports independent consumers
* Bad, because Requires service operation
* Bad, because Batch result access still needs a delivery contract
* Sources: `s02_p10`, `s02_p12`, `s19_p14`

### gRPC model interface

* Good, because Defined service interface
* Good, because Supports independent deployment
* Bad, because Requires compatible clients
* Bad, because Less directly grounded for batch consumers
* Sources: `s07_p01`
