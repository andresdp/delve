# Use a durable queue for bursty document classification

* System: Large-scale document classification

## Context and Problem Statement

Daily volume reaches millions and varies strongly by season. A queue can absorb bursts and let classification workers scale independently.

## Decision Drivers

* Millions daily
* Seasonal volume

## Considered Options

* Durable work queue
* Synchronous request processing

## Decision Outcome

Chosen option: "Durable work queue".

Buffering and independent worker scaling address large, seasonally variable volume.

### Consequences

* Classification is asynchronous.
* Queue lag needs operational monitoring.

## Pros and Cons of the Options

### Durable work queue

* Good, because Buffers bursts
* Good, because Decouples workers
* Bad, because Queue operations
* Bad, because Added processing delay

### Synchronous request processing

* Good, because Direct response path
* Bad, because Burst sensitive
* Bad, because Tightly couples services
