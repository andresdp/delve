# Queue-based workers

*How should classification work be dispatched?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily and volume varies strongly over the year. A dispatch model must handle peaks while making efficient use of capacity.

## Decision Drivers

* Millions of documents daily
* Strong seasonal volume variation

## Considered Options

* Queue-based workers
* Synchronous service

## Decision Outcome

Chosen option: "Queue-based workers".

Seasonal scale decides the choice: queued work can be processed by a variable worker pool. This gives up the immediate completion of synchronous requests.

### Consequences

* Results may be delayed during backlogs.
* Workers need capacity management.

## Pros and Cons of the Options

### Queue-based workers

* Good, because Seasonal scale: workers can scale out
* Bad, because Latency: queueing can add delay

### Synchronous service

* Good, because Latency: immediate request path
* Bad, because Seasonal scale: peak capacity must be ready
