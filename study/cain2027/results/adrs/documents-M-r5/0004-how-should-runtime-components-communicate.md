# How should runtime components communicate?

* System: Large-scale document classification

## Context and Problem Statement

Classification, result storage, and multiple consuming teams need to operate independently as demand varies.

## Decision Drivers

* Variable workload
* Several consuming teams

## Considered Options

* Asynchronous message-driven serving (`v:25.2`)
* Stateless horizontally scaled serving (`v:25.1`)

## Decision Outcome

Chosen option: "Asynchronous message-driven serving" (`v:25.2`).

Choose asynchronous messaging to decouple classification from downstream consumption and absorb variable load. “Architecting a Machine Learning System for Risk” and “Machine Learning in Production: Software Architecture” support this approach. The combination check flagged the serving interface as a prerequisite; a REST prediction microservice is selected below.

### Consequences

* Define delivery, retry, and duplicate-handling behavior.
* Consumers must handle asynchronous results.

## Pros and Cons of the Options

### Asynchronous message-driven serving

* Good, because Decouples producers and consumers
* Good, because Buffers bursts
* Bad, because Requires queue operations
* Bad, because Results arrive asynchronously
* Sources: `s10_p04`, `s16_p04`, `s16_p05`

### Stateless horizontally scaled serving

* Good, because Scales by adding replicas
* Good, because Independent request handling
* Bad, because Does not itself buffer bursts
* Bad, because Requires a synchronous caller
* Sources: `s01_p02`, `s04_p01`
