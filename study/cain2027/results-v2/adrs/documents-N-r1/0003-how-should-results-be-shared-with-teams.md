# How should results be shared with teams?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results. A shared publication path can serve them without coupling classification to each team's interface.

## Decision Drivers

* Several teams consume results
* Millions of documents daily

## Considered Options

* Shared result store with read access
* Publish results to each team

## Decision Outcome

Chosen option: "Shared result store with read access".

Multiple consumers decide the choice: a shared result source avoids separate delivery paths for each team. This gives up independent delivery and requires the store to serve concurrent readers.

### Consequences

* Teams depend on shared access.
* Read capacity must handle consumer demand.

## Pros and Cons of the Options

### Shared result store with read access

* Good, because Multiple consumers: one shared source
* Bad, because Scale: readers may compete for resources

### Publish results to each team

* Good, because Multiple consumers: independent delivery
* Bad, because Scale: delivery work grows with consumers
