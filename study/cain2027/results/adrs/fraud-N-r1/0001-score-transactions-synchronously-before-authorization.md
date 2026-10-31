# Score transactions synchronously before authorization

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a fraud score before it is authorized, with latency in the tens of milliseconds.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency

## Considered Options

* Synchronous request-response scoring
* Asynchronous scoring after authorization

## Decision Outcome

Chosen option: "Synchronous request-response scoring".

A score must be available before authorization, and the brief sets a tight response-time target.

### Consequences

* Authorization depends on the scoring path meeting its latency target.

## Pros and Cons of the Options

### Synchronous request-response scoring

* Good, because Score available before authorization
* Good, because Direct latency measurement
* Bad, because Scoring delays authorization
* Bad, because Depends on service availability

### Asynchronous scoring after authorization

* Good, because Decouples scoring from authorization
* Good, because Absorbs bursts
* Bad, because Score arrives too late
* Bad, because Cannot gate authorization
