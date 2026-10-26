# Publish results through a shared result store

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the same classifications. A shared durable interface avoids coupling inference workers to each consumer.

## Decision Drivers

* Consumers: several teams
* Throughput: millions/day

## Considered Options

* Shared durable result store
* Directly call each consumer

## Decision Outcome

Chosen option: "Shared durable result store".

Multiple independent consuming teams decide the choice; durable shared access costs an additional storage component and persistence step.

### Consequences

* A result schema and access controls are needed.
* Retention and replay policies must be set.

## Pros and Cons of the Options

### Shared durable result store

* Good, because Consumers: independent reads
* Good, because Throughput: decouples inference from reads
* Bad, because Operations: store to operate
* Bad, because Latency: persistence adds a step

### Directly call each consumer

* Good, because Latency: direct delivery
* Good, because Operations: no shared store
* Bad, because Consumers: tight coupling
* Bad, because Throughput: fan-out load on inference
