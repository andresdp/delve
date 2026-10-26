# Classification result interface

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classifier’s results, so the system needs a stable way to expose them. The brief does not specify each team’s integration pattern.

## Decision Drivers

* Multiple consumers
* Shared results
* Integration

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

REST provides a broadly consumable interface for the several teams named in the brief. “How to power up your product by machine learning with python microservice, pt. 1” documents API-backed model services; the checked combination was unattested.

### Consequences

* Teams integrate through a shared prediction contract.
* Service availability and interface changes need operational ownership.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Common application interface
* Good, because Separates model from consumers
* Bad, because Requires service operations
* Sources: `s01_p05`, `s01_p08`

### gRPC model interface

* Good, because Supports independent deployment
* Good, because Typed interface
* Bad, because Requires compatible clients
* Sources: `s02_p13`
