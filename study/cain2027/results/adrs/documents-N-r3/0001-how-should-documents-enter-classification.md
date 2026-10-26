# How should documents enter classification?

* System: Large-scale document classification

## Context and Problem Statement

The system must classify millions of incoming documents each day. The brief does not prescribe a transport mechanism.

## Decision Drivers

* High daily volume
* Incoming documents

## Considered Options

* Queued asynchronous ingestion
* Synchronous request processing

## Decision Outcome

Chosen option: "Queued asynchronous ingestion".

Buffering and decoupling suit high volume with strong seasonal variation, while allowing producers to submit documents without waiting for classification.

### Consequences

* Classification results arrive asynchronously.
* Queue capacity and backlog need operational monitoring.

## Pros and Cons of the Options

### Queued asynchronous ingestion

* Good, because Buffers bursts
* Good, because Decouples producers
* Bad, because Adds queue operations
* Bad, because Results are delayed

### Synchronous request processing

* Good, because Simple request flow
* Good, because Immediate response
* Bad, because Tightly couples callers
* Bad, because Harder to absorb bursts
