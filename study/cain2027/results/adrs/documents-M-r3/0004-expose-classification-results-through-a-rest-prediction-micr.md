# Expose classification results through a REST prediction microservice

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classification results, so they need a shared interface to access them.

## Decision Drivers

* Several consuming teams
* Shared access interface
* Independent integration

## Considered Options

* REST prediction microservice (`v:29.1`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST microservice provides multiple teams a common integration point. Sources describe this interface as a way to integrate applications with deployed prediction services; the batch output can also be persisted for scheduled consumption.

### Consequences

* The service contract must remain stable for consumers.
* Service availability becomes a dependency.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Provides an API for integration
* Good, because Separates model access from consumers
* Bad, because Requires service operations
* Sources: `s01_p05`, `s01_p08`, `s02_p10`, `s02_p11`, `s02_p12`

### PMML-based model serving

* Good, because Portable model representation
* Good, because Supports batch and online scoring
* Bad, because Requires compatible tooling
* Sources: `s02_p10`, `s02_p11`
