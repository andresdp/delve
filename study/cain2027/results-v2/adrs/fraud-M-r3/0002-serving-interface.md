# Serving interface

* System: Card-fraud scoring service

## Context and Problem Statement

The payments authorization flow needs to submit transaction features and receive a fraud score synchronously. The interface must fit within the brief’s short response window.

## Decision Drivers

* Latency: tens of milliseconds
* Availability: peak traffic

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

The synchronous authorization flow makes a direct API request the clearest fit, and REST prediction microservices are described in “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2.” We accept network-call overhead to keep the model independently deployable.

### Consequences

* Authorization depends on the prediction service response.
* The API contract must carry transaction inputs and return a score.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Availability: separates and independently deploys prediction service
* Good, because Latency: direct request and response
* Bad, because Latency: service and network calls add overhead
* Sources: `s01_p05`, `s02_p10`, `s02_p11`

### gRPC model interface

* Good, because Latency: direct service-to-service interface
* Good, because Availability: independently deployed model
* Bad, because Availability: requires compatible clients and service setup
* Sources: `s16_p03`, `s16_p04`

### PMML-based model serving

* Good, because Availability: portable model representation
* Good, because Latency: supports online scoring
* Bad, because Availability: requires compatible PMML tooling
* Sources: `s10_p03`, `s10_p04`
