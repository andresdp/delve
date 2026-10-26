# Score transactions inline before authorization

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs a fraud score before it proceeds, and scores must return within tens of milliseconds. An asynchronous scoring path would not meet that sequence.

## Decision Drivers

* Low latency
* Score before authorization

## Considered Options

* Synchronous scoring request
* Asynchronous scoring queue

## Decision Outcome

Chosen option: "Synchronous scoring request".

Scoring before authorization decides the choice. This gives up the queue's ability to absorb bursts, so the synchronous path must be sized and managed for peak traffic.

### Consequences

* Authorization depends on the scoring path's response time.
* The scoring service needs capacity for peak request rates.

## Pros and Cons of the Options

### Synchronous scoring request

* Good, because Low latency: score available in authorization path
* Bad, because Peak availability: scoring delays can delay authorization

### Asynchronous scoring queue

* Good, because Peak availability: buffers traffic bursts
* Bad, because Score before authorization: result may arrive too late
