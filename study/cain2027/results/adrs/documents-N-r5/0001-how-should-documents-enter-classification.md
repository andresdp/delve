# How should documents enter classification?

* System: Large-scale document classification

## Context and Problem Statement

The system handles millions of documents daily, with volume that varies strongly by season. Processing asynchronously can absorb bursts without requiring every consumer to wait for classification.

## Decision Drivers

* millions per day
* seasonal volume
* multiple consumers

## Considered Options

* Synchronous request path
* Durable queue with workers

## Decision Outcome

Chosen option: "Durable queue with workers".

A durable queue buffers seasonal surges and lets classification capacity scale independently of document producers.

### Consequences

* Producers need an acknowledgement and retry contract.
* Queue depth and processing lag need monitoring.

## Pros and Cons of the Options

### Synchronous request path

* Good, because simple flow
* Good, because immediate result
* Bad, because burst-sensitive
* Bad, because couples producers to inference

### Durable queue with workers

* Good, because absorbs bursts
* Good, because decouples producers
* Bad, because adds queue operations
* Bad, because results arrive later
