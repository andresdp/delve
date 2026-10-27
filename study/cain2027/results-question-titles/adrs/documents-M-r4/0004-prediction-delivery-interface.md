# Prediction delivery interface

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so the system needs a defined way to expose predictions. The brief does not specify how those teams integrate.

## Decision Drivers

* multiple consumers
* shared results

## Considered Options

* REST prediction microservice (`v:29.1`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST interface is a broadly supported option for exposing model predictions to multiple application consumers. “How to power up your product by machine learning with python microservice” and “Three Levels of ML Software” document this approach.

### Consequences

* Consumers integrate through an API.
* Service ownership and access patterns remain to be specified.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because supports application integration
* Good, because well represented in evidence
* Bad, because requires service operation
* Sources: `s01_p05`, `s02_p10`, `s19_p14`

### PMML-based model serving

* Good, because portable model representation
* Good, because supports batch and online scoring
* Bad, because requires compatible tooling
* Sources: `s02_p12`
