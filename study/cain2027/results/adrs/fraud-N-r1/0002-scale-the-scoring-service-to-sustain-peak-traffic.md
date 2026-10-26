# Scale the scoring service to sustain peak traffic

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring must continue during peaks while meeting a tight response-time target.

## Decision Drivers

* Peak availability
* Low latency

## Considered Options

* Replicated stateless service
* Single scoring instance
* Queued scoring workers

## Decision Outcome

Chosen option: "Replicated stateless service".

Replicas can add capacity for peaks and avoid a single scoring instance becoming a failure point; keeping requests synchronous supports the latency requirement.

### Consequences

* Replicas need consistent model versions.
* Capacity and health management are required.

## Pros and Cons of the Options

### Replicated stateless service

* Good, because Horizontal scaling
* Good, because No shared request state
* Bad, because Requires managed model distribution

### Single scoring instance

* Good, because Simple deployment
* Good, because No replication coordination
* Bad, because Limited peak capacity
* Bad, because Single failure point

### Queued scoring workers

* Good, because Buffers traffic bursts
* Good, because Decouples intake from compute
* Bad, because Adds queue delay
* Bad, because May miss authorization deadline
