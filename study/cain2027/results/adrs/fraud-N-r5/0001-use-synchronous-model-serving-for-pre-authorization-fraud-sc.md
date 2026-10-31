# Use synchronous model serving for pre-authorization fraud scores

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a score before authorization, with a response time in the tens of milliseconds. A synchronous request lets the authorization flow use the score directly.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Synchronous scoring API
* Asynchronous scoring queue

## Decision Outcome

Chosen option: "Synchronous scoring API".

It returns a usable score in the authorization path and best fits the stated latency requirement. The service must be provisioned and monitored to keep that dependency responsive.

### Consequences

* Authorization depends on scoring availability
* Scoring latency needs a defined budget

## Pros and Cons of the Options

### Synchronous scoring API

* Good, because Immediate score
* Good, because Simple authorization flow
* Bad, because Adds a dependency
* Bad, because Needs strict latency control

### Asynchronous scoring queue

* Good, because Buffers bursts
* Good, because Decouples services
* Bad, because Score arrives later
* Bad, because Complicates authorization
