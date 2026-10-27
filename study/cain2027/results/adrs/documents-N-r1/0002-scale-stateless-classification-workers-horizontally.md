# Scale stateless classification workers horizontally

* System: Large-scale document classification

## Context and Problem Statement

Classification demand varies over the year, and the system must process millions of documents per day. Stateless workers can scale with queued demand.

## Decision Drivers

* Seasonal peaks
* Daily volume
* Processing capacity

## Considered Options

* Horizontally scaled stateless workers
* Fixed-capacity worker fleet

## Decision Outcome

Chosen option: "Horizontally scaled stateless workers".

A horizontally scaled pool can add throughput for seasonal peaks and reduce idle capacity outside them.

### Consequences

* Worker scaling must respect LLM rate limits.
* Define limits for backlog age and scale-up time.

## Pros and Cons of the Options

### Horizontally scaled stateless workers

* Good, because Scales with demand
* Good, because Simple recovery
* Bad, because Needs capacity controls

### Fixed-capacity worker fleet

* Good, because Predictable capacity
* Bad, because Overprovisioned off-peak
* Bad, because May fall behind at peaks
