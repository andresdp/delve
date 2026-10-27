# Expose classification through a REST prediction microservice

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classification results, so the model needs a shared integration boundary. The brief does not specify synchronous versus asynchronous delivery.

## Decision Drivers

* Several consuming teams
* Shared prediction access

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST service gives multiple teams a common prediction interface. The chosen interface is supported by sources, but the complete combination was unattested in the design-point check.

### Consequences

* Maintain a stable request and response contract.
* Scale and monitor the serving service.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because API integration
* Good, because Independent deployment
* Bad, because Requires service operations
* Sources: `s02_p10`, `s02_p11`

### gRPC model interface

* Good, because Independent deployment
* Good, because Typed service interface
* Bad, because Client integration required
* Sources: `s19_p14`, `s21_p10`
