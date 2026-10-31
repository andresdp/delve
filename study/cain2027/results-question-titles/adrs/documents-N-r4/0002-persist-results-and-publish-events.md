# Persist results and publish events

*How should results be shared with consuming teams?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so the system needs a stable way to distribute them without coupling each consumer to classifier internals.

## Decision Drivers

* Several consuming teams
* Shared classification results

## Considered Options

* Direct calls to each consumer
* Persist results and publish events

## Decision Outcome

Chosen option: "Persist results and publish events".

Persisting each result and publishing an event gives multiple teams independent access while preserving results for recovery or replay.

### Consequences

* Define a versioned result schema.
* Operate result storage and event delivery.

## Pros and Cons of the Options

### Direct calls to each consumer

* Good, because Straightforward delivery
* Good, because Consumers receive results promptly
* Bad, because Classifier couples to consumers
* Bad, because Consumer outages disrupt delivery

### Persist results and publish events

* Good, because Consumers evolve independently
* Good, because Results can be replayed
* Bad, because Requires storage and event operations
* Bad, because Consumers handle duplicate events
