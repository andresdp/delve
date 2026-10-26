# Model runtime placement

* System: Card-fraud scoring service

## Context and Problem Statement

The transaction authorization path needs a real-time prediction interface that the payments application can call. A model bundled into the application would couple its release cycle to the application’s.

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Model-as-a-service deployment (`v:30.3`)
* Model-as-dependency deployment (`v:30.18`)

## Decision Outcome

Chosen option: "Model-as-a-service deployment" (`v:30.3`).

Peak availability decides the choice: independent serving capacity can scale with scoring demand. The system gives up the lower latency and simpler operation of an in-process model call, so the service hop must fit the latency budget.

### Consequences

* Keep model serving independently deployable and scalable.
* Include service-call overhead in the scoring latency budget.

## Pros and Cons of the Options

### Model-as-a-service deployment

* Good, because Low latency: exposes a direct real-time prediction service
* Good, because Peak availability: serving can scale independently
* Bad, because Low latency: adds a network call
* Bad, because Peak availability: introduces a service dependency
* Sources: `s01_p06`, `s01_p08`, `s06_p13`, `s19_p08`

### Model-as-dependency deployment

* Good, because Low latency: avoids a service network hop
* Good, because Peak availability: model ships with the application
* Bad, because Peak availability: application capacity also carries scoring load
* Bad, because Audit traceability: model updates follow application releases
* Sources: `s01_p05`, `s02_p10`, `s09_p09`
