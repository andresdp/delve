# How should classification results reach consuming teams?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, but the brief does not specify their integration patterns or latency needs.

## Decision Drivers

* Several consumer teams
* High result volume

## Considered Options

* Publish results to a shared event stream
* Expose a shared query API

## Decision Outcome

Chosen option: "Publish results to a shared event stream".

A shared stream lets multiple teams consume results independently without coupling classification to each team's access patterns.

### Consequences

* Consumers must manage their own progress and retries.
* Result schema changes affect multiple teams.

## Pros and Cons of the Options

### Publish results to a shared event stream

* Good, because Consumers are decoupled
* Good, because Supports multiple teams
* Bad, because Requires consumer handling
* Bad, because Delivery semantics need design

### Expose a shared query API

* Good, because Central access point
* Good, because Consumers query as needed
* Bad, because Adds request load
* Bad, because Requires availability coordination
