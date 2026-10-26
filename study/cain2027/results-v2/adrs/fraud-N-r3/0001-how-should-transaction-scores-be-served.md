# How should transaction scores be served?

* System: Card-fraud scoring service

## Context and Problem Statement

The service scores every transaction before authorization, with responses due within tens of milliseconds. Priority requirements are low latency, peak resilience, and auditability.

## Decision Drivers

* Low latency
* Peak resilience
* Auditability

## Considered Options

* Synchronous in-process model scoring
* Synchronous dedicated scoring service
* Asynchronous scoring

## Decision Outcome

Chosen option: "Synchronous in-process model scoring".

Low latency decides the choice because scoring must finish before authorization within tens of milliseconds. This gives up isolation and independent scaling during peaks.

### Consequences

* Scoring capacity scales with the authorization service.
* Model loading and runtime affect the transaction process.

## Pros and Cons of the Options

### Synchronous in-process model scoring

* Good, because Low latency: avoids network hop
* Bad, because Peak resilience: shares service capacity

### Synchronous dedicated scoring service

* Good, because Peak resilience: scales scoring separately
* Bad, because Low latency: adds network hop

### Asynchronous scoring

* Good, because Peak resilience: buffers bursts
* Bad, because Low latency: delays authorization decision
