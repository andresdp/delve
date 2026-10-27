# Integrate the classifier as an event-driven service

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so the model should be decoupled from individual applications. The design space describes an event-driven model service as using a pub/sub or queueing interface.

## Decision Drivers

* Multiple consuming teams
* Decoupled integration
* High volume

## Considered Options

* Event-driven model as a service (`v:1.5`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Event-driven model as a service" (`v:1.5`).

An event-driven interface supports multiple consumers and is compatible with the batch-oriented point checked. The checked point has no warnings; the service-based rival also has no warnings, but does not express the decoupled queueing interface as directly.

### Consequences

* Events or queued work need stable identifiers.
* Consumers must handle delayed result availability.

## Pros and Cons of the Options

### Event-driven model as a service

* Good, because Queue or pub/sub interface
* Good, because Decouples producers and consumers
* Bad, because Requires event coordination
* Sources: `d:1`, `v:1.5`

### Model as a service

* Good, because Separate model service
* Good, because Direct service boundary
* Bad, because Synchronous coupling risk
* Sources: `d:1`, `v:1.1`
