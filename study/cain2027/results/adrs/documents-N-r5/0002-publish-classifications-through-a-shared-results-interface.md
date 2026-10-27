# Publish classifications through a shared results interface

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results. A shared, stable interface avoids coupling each consumer to classifier internals.

## Decision Drivers

* Several consumers
* Shared results

## Considered Options

* Directly integrate each consumer
* Shared results API
* Publish result events

## Decision Outcome

Chosen option: "Shared results API".

A shared API gives multiple teams a consistent way to retrieve results while keeping classifier implementation behind a boundary.

### Consequences

* The API needs a stable contract.
* Access patterns and availability targets remain to be defined.

## Pros and Cons of the Options

### Directly integrate each consumer

* Good, because Tailored integrations
* Bad, because Many integrations to maintain
* Bad, because Consumers couple to classifier

### Shared results API

* Good, because Consistent access path
* Good, because Consumers stay decoupled
* Bad, because Requires API ownership
* Bad, because Consumers depend on its availability

### Publish result events

* Good, because Consumers process independently
* Good, because Supports multiple subscribers
* Bad, because Requires event operations
* Bad, because Consumers manage delivery
