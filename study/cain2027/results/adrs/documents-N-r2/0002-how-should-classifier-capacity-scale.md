# How should classifier capacity scale?

* System: Large-scale document classification

## Context and Problem Statement

Daily volume reaches millions and changes substantially through the year. The system needs to expand capacity during peaks without keeping peak-sized resources year-round.

## Decision Drivers

* Millions daily
* Seasonal volume
* Classification throughput

## Considered Options

* Statically sized inference fleet
* Autoscaled inference workers

## Decision Outcome

Chosen option: "Autoscaled inference workers".

Autoscaled workers better match the strong seasonal variation while supporting high daily throughput.

### Consequences

* Scaling signals and limits need configuration.
* Peak capacity must be provisioned and monitored.

## Pros and Cons of the Options

### Statically sized inference fleet

* Good, because Predictable capacity
* Good, because Simple operations
* Bad, because Pays for idle capacity
* Bad, because May fall behind at peaks

### Autoscaled inference workers

* Good, because Matches changing demand
* Good, because Scales independently
* Bad, because Scaling lag
* Bad, because Capacity limits need tuning
