# Model as a service

*How to integrate the model?*

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a score before authorization, so the application needs an online model interface. The design space includes service-based and in-application integration patterns (d:1).

## Decision Drivers

* Tens-of-ms latency
* Peak availability

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)
* Event-driven model as a service (`v:1.5`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

Peak availability decides the choice: a separately scalable service isolates scoring capacity, at the cost of a network hop that must fit the latency budget.

### Consequences

* Operate scoring capacity independently.
* Keep the synchronous request path within the latency budget.

## Pros and Cons of the Options

### Model as a service

* Good, because Peak availability: scale service independently
* Bad, because Latency: network hop
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because Latency: in-process call
* Bad, because Peak availability: scales with application
* Sources: `d:1`, `v:1.2`

### Event-driven model as a service

* Good, because Peak availability: decoupled processing
* Bad, because Latency: asynchronous response path
* Sources: `d:1`, `v:1.5`
