# Store inputs and predictions in a shared data store

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so the system needs a shared access path. Shared stores and event stores are options in the design space (d:2).

## Decision Drivers

* Several consuming teams
* Daily document volumes
* Batch results

## Considered Options

* Shared data store (`v:2.1`)
* Event store (`v:2.3`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

A shared store directly supports multiple teams consuming completed batch predictions. The checked point had no attesting systems, so the combination is novel in the design space.

### Consequences

* Teams need a common result schema.
* Storage retention and access policies need definition.

## Pros and Cons of the Options

### Shared data store

* Good, because Shared access path
* Good, because Fits batch result storage
* Bad, because Requires shared data conventions
* Sources: `d:2`, `v:2.1`

### Event store

* Good, because Stores events as exchanged
* Good, because Supports event consumers
* Bad, because Event consumption model required
* Sources: `d:2`, `v:2.3`
