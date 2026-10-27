# Scale classification workers horizontally for variable volume

* System: Large-scale document classification

## Context and Problem Statement

Daily volume reaches millions and varies strongly over the year, so processing capacity must adapt to demand.

## Decision Drivers

* Millions of documents daily
* Seasonal volume variation

## Considered Options

* Horizontally scaled workers
* Fixed-capacity workers

## Decision Outcome

Chosen option: "Horizontally scaled workers".

Adjustable parallel capacity better accommodates seasonal changes in document volume.

### Consequences

* Requires worker scaling controls
* Peak demand still needs capacity planning

## Pros and Cons of the Options

### Horizontally scaled workers

* Good, because Adjustable capacity
* Good, because Parallel processing
* Bad, because Scaling operations
* Bad, because Capacity changes may lag

### Fixed-capacity workers

* Good, because Simple to operate
* Good, because Stable capacity
* Bad, because Peak overload risk
* Bad, because Idle capacity off peak
