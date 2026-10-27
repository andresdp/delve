# Scale stateless classifier workers horizontally

* System: Large-scale document classification

## Context and Problem Statement

The classifier must process millions of documents per day while demand varies over the year. Stateless workers can be added or removed as queue demand changes.

## Decision Drivers

* Millions daily
* Seasonal volume

## Considered Options

* Horizontally scaled stateless workers
* Fixed-capacity worker pool

## Decision Outcome

Chosen option: "Horizontally scaled stateless workers".

Elastic workers match seasonal demand while keeping the classifier separate from ingestion and consumers.

### Consequences

* Worker count must track backlog and capacity.
* Model serving capacity constrains scale.

## Pros and Cons of the Options

### Horizontally scaled stateless workers

* Good, because Elastic capacity
* Good, because Independent deployment
* Bad, because Scaling complexity
* Bad, because Model capacity limits

### Fixed-capacity worker pool

* Good, because Predictable capacity
* Good, because Simple operations
* Bad, because Peak overprovisioning
* Bad, because May fall behind at peaks
