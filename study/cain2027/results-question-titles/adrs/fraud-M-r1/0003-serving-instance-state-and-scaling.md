# Serving instance state and scaling

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring traffic varies with transaction volume, and the service must remain available during peaks. Independent request handling allows capacity to grow by adding serving instances.

## Decision Drivers

* Peak availability
* Horizontal scaling
* Low latency

## Considered Options

* Stateless horizontally scaled serving (`v:25.1`)
* Horizontally scaled Redis-backed asynchronous serving (`v:25.3`)

## Decision Outcome

Chosen option: "Stateless horizontally scaled serving" (`v:25.1`).

Stateless replicas fit variable peaks and keep the scoring workers independently scalable. “How to power up your product by machine learning with python microservice” and “Productionizing Machine Learning with a Microservices Architecture” support this approach.

### Consequences

* Keep durable state and feature data in external stores.
* Scale replicas against measured traffic and latency.

## Pros and Cons of the Options

### Stateless horizontally scaled serving

* Good, because Scale by adding replicas
* Good, because Independent request handling
* Bad, because Shared state must live elsewhere
* Bad, because Replica capacity needs monitoring
* Sources: `s01_p02`, `s04_p01`

### Horizontally scaled Redis-backed asynchronous serving

* Good, because Combines scalable serving and shared storage
* Good, because Decouples work through messages
* Bad, because Adds storage and queue dependencies
* Bad, because May add latency
