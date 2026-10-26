# How should inference scale with seasonal demand?

* System: Large-scale document classification

## Context and Problem Statement

Classification volume varies strongly over the year, so fixed capacity risks being insufficient during peaks or underused otherwise.

## Decision Drivers

* Seasonal volume variation
* Millions per day

## Considered Options

* Autoscaled stateless workers
* Fixed worker fleet

## Decision Outcome

Chosen option: "Autoscaled stateless workers".

Stateless workers can expand or contract as queued work changes, aligning capacity with seasonal demand.

### Consequences

* Worker scaling signals and limits must be configured.
* Peak bursts may still create processing delays.

## Pros and Cons of the Options

### Autoscaled stateless workers

* Good, because Scales with demand
* Good, because Workers can be replaced
* Bad, because Scaling has lag
* Bad, because Capacity limits still apply

### Fixed worker fleet

* Good, because Predictable capacity
* Good, because Simpler scaling behavior
* Bad, because Peak overprovisioning
* Bad, because Peak capacity may be insufficient
