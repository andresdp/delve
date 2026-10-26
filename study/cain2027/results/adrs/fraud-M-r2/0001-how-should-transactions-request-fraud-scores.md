# How should transactions request fraud scores?

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs a score within tens of milliseconds. The interface must support synchronous scoring and clear integration with payment processing.

## Decision Drivers

* Tens-of-milliseconds latency
* Authorization-time scoring

## Considered Options

* REST prediction microservice (`v:29.1`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

It provides a direct synchronous API for authorization-time scoring. Sources such as “How to power up your product by machine learning with python microservice” and “Architecting a Machine Learning Pipeline” describe this service pattern.

### Consequences

* Payment processing depends on the scoring endpoint.
* The service must return within the authorization latency budget.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Simple service integration
* Good, because Separates model deployment
* Bad, because Network hop adds latency
* Bad, because Requires service availability
* Sources: `s01_p05`, `s02_p10`

### PMML-based model serving

* Good, because Portable model representation
* Good, because Supports online and batch scoring
* Bad, because Compatible tooling required
* Sources: `s02_p13`
