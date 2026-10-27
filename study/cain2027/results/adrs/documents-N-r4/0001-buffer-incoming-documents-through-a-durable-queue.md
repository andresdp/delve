# Buffer incoming documents through a durable queue

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of incoming documents per day, and volume varies strongly over the year. A durable buffer separates intake from classification capacity.

## Decision Drivers

* Millions daily
* Seasonal volume

## Considered Options

* Durable queue
* Synchronous processing

## Decision Outcome

Chosen option: "Durable queue".

A queue buffers seasonal peaks and lets classification capacity scale independently of intake.

### Consequences

* Queued documents need retry handling.
* Classification results arrive asynchronously.

## Pros and Cons of the Options

### Durable queue

* Good, because Absorbs bursts
* Good, because Decouples intake
* Bad, because Adds infrastructure

### Synchronous processing

* Good, because Simple flow
* Bad, because Intake tied to capacity
