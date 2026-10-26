# REST prediction microservice

*How should teams access classification results?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classifications, so the system needs a shared integration boundary. Since the selected prediction mode is batch, an API can expose persisted results without requiring online scoring.

## Decision Drivers

* Multiple consumers
* High daily volume

## Considered Options

* REST prediction microservice (`v:29.1`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

Multiple consumers decide the choice: a REST interface offers a shared application boundary, as described in “How to power up your product by machine learning with python microservice” and “Architecting a Machine Learning Pipeline.” The service exposes completed batch results; it does not require synchronous scoring for every document.

### Consequences

* Publish a stable result schema and access contract.
* Control access for each consuming team.
* Persist batch outputs behind the service.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Multiple consumers: common application interface
* Good, because Integration: separates callers from model implementation
* Bad, because High volume: request traffic can burden serving
* Sources: `s01_p05`, `s02_p10`, `s09_p03`

### PMML-based model serving

* Good, because Integration: portable model representation
* Bad, because Multiple consumers: requires compatible tooling
* Sources: `s02_p12`, `s15_p04`
