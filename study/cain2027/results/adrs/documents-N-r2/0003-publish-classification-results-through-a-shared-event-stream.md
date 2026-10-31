# Publish classification results through a shared event stream

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results. Publishing each completed classification to a shared stream decouples consumers from classifier execution.

## Decision Drivers

* Several consumers
* High volume

## Considered Options

* Shared result event stream
* Direct calls to each consumer
* Shared results database

## Decision Outcome

Chosen option: "Shared result event stream".

A shared stream lets teams consume results independently and accommodates multiple downstream consumers.

### Consequences

* A versioned result contract is needed.
* Delivery and replay behavior must be defined.

## Pros and Cons of the Options

### Shared result event stream

* Good, because Fan-out to consumers
* Good, because Consumer independence
* Bad, because Stream operations
* Bad, because Delivery semantics to define

### Direct calls to each consumer

* Good, because Simple for few consumers
* Bad, because Consumer coupling
* Bad, because Fan-out failures affect processing

### Shared results database

* Good, because Supports queries
* Good, because Single result store
* Bad, because Schema coupling
* Bad, because Consumer load concentration
