# How should results be exposed to consuming teams?

* System: Large-scale document classification

## Context and Problem Statement

The brief names several result consumers but does not specify their integration protocols. A shared prediction API offers a concrete integration boundary.

## Decision Drivers

* Several consuming teams
* Shared classification results

## Considered Options

* REST prediction microservice (`v:29.1`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

Choose the REST prediction microservice as the interface decision required by the runtime communication choice. “How to power up your product by machine learning with python microservice, pt. 1” and “Productionizing Machine Learning with a Microservices Architecture” support an API-backed boundary; the exact protocol needs confirmation with consumers.

### Consequences

* Publish a stable request and response contract.
* Specify how batch results are retrieved through the interface.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Common application integration boundary
* Good, because Separates model from consumers
* Bad, because Requires service availability
* Bad, because Does not define batch delivery cadence
* Sources: `s01_p02`, `s04_p01`

### PMML-based model serving

* Good, because Portable model representation
* Good, because Supports batch and online scoring
* Bad, because Consumers need compatible tooling
* Bad, because Does not define result access patterns
* Sources: `s02_p11`
