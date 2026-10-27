# Scale stateless scoring instances horizontally

* System: Card-fraud scoring service

## Context and Problem Statement

The service must continue handling transaction traffic during peaks. Independent request handling allows capacity to grow by adding serving replicas.

## Decision Drivers

* Peak availability
* Independent requests

## Considered Options

* Stateless horizontally scaled serving (`v:25.1`)
* Asynchronous message-driven serving (`v:25.2`)

## Decision Outcome

Chosen option: "Stateless horizontally scaled serving" (`v:25.1`).

Choose stateless replicas to preserve synchronous scoring while scaling capacity. “Productionizing Machine Learning with a Microservices Architecture” supports stateless serving; the design point reported no warnings, though the full combination was unattested.

### Consequences

* Keep durable feature state outside serving instances.
* Define health checks and capacity limits.

## Pros and Cons of the Options

### Stateless horizontally scaled serving

* Good, because Independent request handling
* Good, because Scale out with replicas
* Bad, because Requires externalized shared data
* Sources: `s01_p02`, `s04_p01`

### Asynchronous message-driven serving

* Good, because Decouples downstream work
* Good, because Absorbs queued work
* Bad, because Can delay authorization response
* Sources: `s04_p03`, `s04_p04`
