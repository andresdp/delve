# Use synchronous online scoring before transaction authorization

* System: Card-fraud scoring service

## Context and Problem Statement

Each card transaction needs a fraud score before authorization, with a tens-of-milliseconds response budget.

## Decision Drivers

* Pre-authorization score
* Tens-of-milliseconds latency
* Transaction peaks

## Considered Options

* Synchronous request-response scoring
* Asynchronous scoring after authorization

## Decision Outcome

Chosen option: "Synchronous request-response scoring".

The score must be available before authorization, so synchronous scoring fits the transaction flow despite its latency and availability demands.

### Consequences

* Scoring becomes part of authorization-path latency
* Capacity must handle peak request volume

## Pros and Cons of the Options

### Synchronous request-response scoring

* Good, because Score available in time
* Good, because Simple transaction flow
* Bad, because Adds authorization-path dependency
* Bad, because Latency budget is tight

### Asynchronous scoring after authorization

* Good, because Decouples transaction path
* Good, because Absorbs traffic bursts
* Bad, because Score arrives too late
* Bad, because Cannot gate authorization
