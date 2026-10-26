# Scale serving capacity for transaction peaks

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring must keep working during peaks, while each result must still arrive within tens of milliseconds. The brief does not specify peak size or request limits.

## Decision Drivers

* Peak availability
* Tens-of-milliseconds latency

## Considered Options

* Autoscale stateless inference replicas
* Maintain fixed excess capacity
* Queue requests when capacity is full

## Decision Outcome

Chosen option: "Autoscale stateless inference replicas".

Peak availability decides the choice: stateless replicas can add scoring capacity as demand rises. This gives up immediate protection from scale-up delay, which must be managed with capacity headroom.

### Consequences

* Keep inference replicas stateless so they can scale horizontally.
* Maintain headroom to cover demand while replicas start.
* Set capacity limits and a policy for requests that exceed them.

## Pros and Cons of the Options

### Autoscale stateless inference replicas

* Good, because Peak availability: add replicas as demand rises
* Good, because Tens-of-milliseconds latency: distribute requests across replicas
* Bad, because Tens-of-milliseconds latency: scale-up delay can expose capacity gaps

### Maintain fixed excess capacity

* Good, because Peak availability: capacity is ready at peak onset
* Good, because Tens-of-milliseconds latency: avoids scale-up delay
* Bad, because Peak availability: excess capacity remains idle off-peak

### Queue requests when capacity is full

* Good, because Peak availability: absorbs short bursts
* Bad, because Tens-of-milliseconds latency: queueing can exceed the scoring budget
