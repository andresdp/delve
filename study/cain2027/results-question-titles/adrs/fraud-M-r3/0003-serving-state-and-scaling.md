# Serving state and scaling

* System: Card-fraud scoring service

## Context and Problem Statement

Traffic peaks require additional scoring capacity, while serving state can complicate scaling and recovery.

## Decision Drivers

* Peak availability
* Horizontal scale
* Low latency

## Considered Options

* Stateless horizontally scaled serving (`v:25.1`)
* Asynchronous message-driven serving (`v:25.2`)

## Decision Outcome

Chosen option: "Stateless horizontally scaled serving" (`v:25.1`).

Independent scoring instances can scale with peaks while keeping the authorization request synchronous; queues risk delaying a score needed before authorization.

### Consequences

* Keep durable features and model artifacts outside serving instances.
* Provide health checks and load balancing for replicas.

## Pros and Cons of the Options

### Stateless horizontally scaled serving

* Good, because Independent request handling
* Good, because Scale by adding replicas
* Bad, because Shared state belongs elsewhere
* Sources: `s01_p02`, `s04_p01`

### Asynchronous message-driven serving

* Good, because Decouples downstream work
* Good, because Non-blocking communication
* Bad, because Queueing may add latency
* Bad, because Less suited to synchronous authorization
* Sources: `s10_p04`, `s16_p04`
