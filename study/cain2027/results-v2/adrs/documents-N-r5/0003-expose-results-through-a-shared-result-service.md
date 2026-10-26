# Expose results through a shared result service

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so each should have a consistent way to access them. The choice also affects how independently consumers can process new classifications.

## Decision Drivers

* Multi-team access
* Millions/day throughput

## Considered Options

* Shared result API backed by durable storage
* Publish results to a shared event stream

## Decision Outcome

Chosen option: "Shared result API backed by durable storage".

Multi-team access decides the choice: a shared interface gives teams a common way to retrieve results. This gives up the independent processing and fan-out benefits of an event stream.

### Consequences

* The result service and storage become shared dependencies.
* Retention and consumer access policies need definition.

## Pros and Cons of the Options

### Shared result API backed by durable storage

* Good, because Multi-team access: one consistent interface
* Good, because Throughput: storage decouples reads from inference
* Bad, because Throughput: API and storage need capacity planning
* Bad, because Operations: service and access controls to maintain

### Publish results to a shared event stream

* Good, because Throughput: consumers process independently
* Good, because Multi-team access: new consumers can subscribe
* Bad, because Multi-team access: each team manages consumption state
* Bad, because Operations: replay and delivery semantics add complexity
