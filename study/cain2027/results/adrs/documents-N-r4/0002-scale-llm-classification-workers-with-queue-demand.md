# Scale LLM classification workers with queue demand

* System: Large-scale document classification

## Context and Problem Statement

Daily volume is large and seasonally variable. Worker capacity needs to follow the backlog while using an LLM-based classifier.

## Decision Drivers

* Millions daily
* Seasonal volume
* LLM classifier

## Considered Options

* Autoscaled worker pool
* Fixed worker pool

## Decision Outcome

Chosen option: "Autoscaled worker pool".

Autoscaling can raise throughput during seasonal peaks and reduce excess capacity when demand falls.

### Consequences

* Capacity signals and scaling limits need configuration.
* LLM service limits constrain peak throughput.

## Pros and Cons of the Options

### Autoscaled worker pool

* Good, because Follows demand
* Good, because Processes in parallel
* Bad, because Scaling needs tuning

### Fixed worker pool

* Good, because Predictable capacity
* Bad, because Peak backlog
* Bad, because Idle off-peak
