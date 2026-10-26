# How should documents reach the classifier?

* System: Large-scale document classification

## Context and Problem Statement

The system must classify millions of incoming documents per day, with strongly seasonal volume. A decoupled queue can absorb bursts and separate intake from model capacity.

## Decision Drivers

* High daily volume
* Seasonal peaks

## Considered Options

* Queued asynchronous pipeline
* Synchronous classification at intake

## Decision Outcome

Chosen option: "Queued asynchronous pipeline".

A queue absorbs seasonal spikes and lets classification capacity scale independently from document intake. Asynchronous processing trades immediate results for resilience under variable load.

### Consequences

* Results arrive after intake.
* Queue depth and processing delay need monitoring.

## Pros and Cons of the Options

### Queued asynchronous pipeline

* Good, because Buffers bursts
* Good, because Scales workers independently
* Bad, because Adds processing delay
* Bad, because Needs retry handling

### Synchronous classification at intake

* Good, because Immediate result
* Good, because Simple flow
* Bad, because Couples intake to model capacity
* Bad, because Peak traffic can overwhelm service
