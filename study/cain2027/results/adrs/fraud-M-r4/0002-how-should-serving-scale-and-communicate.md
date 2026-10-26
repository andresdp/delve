# How should serving scale and communicate?

* System: Card-fraud scoring service

## Context and Problem Statement

Peak demand requires the scoring service to absorb changing load without depending on one serving instance. The checked design point pairs stateless horizontal scaling with a prediction service interface.

## Decision Drivers

* Peak availability
* Changing demand
* Low latency

## Considered Options

* Stateless horizontally scaled serving (`v:25.1`)
* Asynchronous message-driven serving (`v:25.2`)

## Decision Outcome

Chosen option: "Stateless horizontally scaled serving" (`v:25.1`).

Independent stateless requests support horizontal scaling and fit the peak-availability driver. The checked point combined this with the queue-fronted online cluster and REST interface; it returned no warnings, though no sources attested to the full combination. “How to power up your product by machine learning with python microservice” supports the stateless option.

### Consequences

* Keep request state outside serving replicas.
* Scale replicas to match incoming demand.

## Pros and Cons of the Options

### Stateless horizontally scaled serving

* Good, because Independent requests
* Good, because Scale by adding replicas
* Bad, because Requires external handling of shared state
* Bad, because Replica capacity must be managed
* Sources: `s01_p02`, `s04_p01`

### Asynchronous message-driven serving

* Good, because Decouples components
* Good, because Non-blocking communication
* Bad, because Queue processing adds complexity
* Bad, because Synchronous authorization latency may be difficult
