# Score synchronously before authorization

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs the fraud score before it can proceed, and the brief sets a tens-of-milliseconds response target.

## Decision Drivers

* Tens-of-milliseconds latency
* Continuous peak operation

## Considered Options

* Synchronous scoring in the authorization path
* Asynchronous scoring after authorization

## Decision Outcome

Chosen option: "Synchronous scoring in the authorization path".

The latency target decides this choice: authorization must receive the score in time to use it. This makes scorer availability part of the authorization path.

### Consequences

* The authorization flow needs a defined timeout and failure behavior.

## Pros and Cons of the Options

### Synchronous scoring in the authorization path

* Good, because Latency: score available before authorization
* Bad, because Availability: scorer failure can delay authorization

### Asynchronous scoring after authorization

* Good, because Availability: authorization need not wait for scoring
* Bad, because Latency: score arrives too late for the authorization decision
