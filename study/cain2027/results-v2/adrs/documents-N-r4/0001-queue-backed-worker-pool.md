# Queue-backed worker pool

*How should classification work scale with demand?*

* System: Large-scale document classification

## Context and Problem Statement

The system processes millions of incoming documents per day, and volume varies strongly over the year. A queue can absorb bursts and let worker capacity scale with demand.

## Decision Drivers

* High volume: millions per day
* Seasonal demand: strong variation

## Considered Options

* Synchronous inference API
* Queue-backed worker pool
* Scheduled bulk batches

## Decision Outcome

Chosen option: "Queue-backed worker pool".

Seasonal demand decides the choice: a queue absorbs peaks while workers scale horizontally. This adds a queueing step and can increase time to results.

### Consequences

* Classification becomes asynchronous.
* Workers need scaling and queue monitoring.
* Result latency depends on backlog and capacity.

## Pros and Cons of the Options

### Synchronous inference API

* Good, because High volume: direct request path
* Bad, because Seasonal demand: callers face capacity spikes

### Queue-backed worker pool

* Good, because Seasonal demand: buffer bursts
* Good, because High volume: scale workers horizontally
* Bad, because High volume: queue adds processing steps

### Scheduled bulk batches

* Good, because High volume: efficient bulk processing
* Bad, because Seasonal demand: capacity changes less responsively
