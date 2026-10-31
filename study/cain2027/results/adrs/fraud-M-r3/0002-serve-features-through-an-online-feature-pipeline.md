# Serve features through an online feature pipeline

* System: Card-fraud scoring service

## Context and Problem Statement

Each authorization request needs its features quickly enough to meet the brief’s tens-of-milliseconds target. Features also need a defined production path into inference.

## Decision Drivers

* Low latency
* Online scoring
* Feature traceability

## Considered Options

* Online feature-serving pipeline (`v:43.2`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online feature-serving pipeline" (`v:43.2`).

A low-latency online store fits synchronous authorization scoring better than an analytical platform alone. Productionizing Machine Learning with a Microservices Architecture and MLOps Principles support shared preparation and online feature serving.

### Consequences

* Keep online feature retrieval on the scoring path.
* Track feature definitions and materialized versions.

## Pros and Cons of the Options

### Online feature-serving pipeline

* Good, because Materializes online features
* Good, because Supports low-latency inference
* Bad, because Requires serving-store operations
* Sources: `s04_p01`, `s22_p03`

### Central analytical ML data platform

* Good, because Shared data platform
* Good, because Supports downstream reuse
* Bad, because Online access not explicit
