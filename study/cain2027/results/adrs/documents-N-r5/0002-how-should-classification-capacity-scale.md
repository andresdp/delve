# How should classification capacity scale?

* System: Large-scale document classification

## Context and Problem Statement

Daily volume varies strongly through the year, while the system must process millions of documents. Capacity needs to follow demand without making peak capacity a year-round requirement.

## Decision Drivers

* seasonal volume
* high throughput

## Considered Options

* Fixed-size worker pool
* Autoscaling worker pool

## Decision Outcome

Chosen option: "Autoscaling worker pool".

Autoscaling workers fit variable demand while keeping throughput adjustable; queue depth and lag can guide scaling.

### Consequences

* Scaling thresholds require tuning.
* Peak capacity still needs a configured ceiling.

## Pros and Cons of the Options

### Fixed-size worker pool

* Good, because predictable capacity
* Good, because simple operations
* Bad, because idle off-peak
* Bad, because may lag at peaks

### Autoscaling worker pool

* Good, because tracks demand
* Good, because reduces idle capacity
* Bad, because scaling lag
* Bad, because needs capacity limits
