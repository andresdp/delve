# How should classification results reach consuming teams?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so each needs a stable way to access them without coupling its workflow directly to the classifier.

## Decision Drivers

* Multiple consumers: several teams
* High volume: millions per day

## Considered Options

* Direct integration from classifier to each team
* Shared results API
* Shared results store with change events

## Decision Outcome

Chosen option: "Shared results store with change events".

Multiple consumers decide the choice: a shared store and events let teams integrate independently. Operating both components adds complexity.

### Consequences

* Define a common result schema.
* Consumers need event handling and store access.
* The store and event path need operational ownership.

## Pros and Cons of the Options

### Direct integration from classifier to each team

* Good, because Multiple consumers: direct delivery
* Bad, because Multiple consumers: integrations multiply with each team

### Shared results API

* Good, because Multiple consumers: one stable interface
* Bad, because High volume: shared API must handle concurrent reads

### Shared results store with change events

* Good, because Multiple consumers: teams can consume independently
* Good, because High volume: decouples reads from inference
* Bad, because Multiple consumers: event and store operations add complexity
