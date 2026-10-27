# Publish classification results as events

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so one processing workflow should serve multiple independent consumers. Events let teams consume results on their own schedules.

## Decision Drivers

* Multiple consumers
* Consumer independence

## Considered Options

* Publish result events
* Direct calls to each consumer

## Decision Outcome

Chosen option: "Publish result events".

Events let teams consume the same classification independently without coupling classifier availability to each consumer.

### Consequences

* Define and version a shared result schema.
* Provide replay and delivery-failure handling.

## Pros and Cons of the Options

### Publish result events

* Good, because Decouples consumers
* Good, because Supports replay
* Bad, because Requires event contracts

### Direct calls to each consumer

* Good, because Immediate delivery
* Bad, because Couples classifier to teams
* Bad, because Consumer failures affect processing
