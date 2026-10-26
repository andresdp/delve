# How should authorization obtain a fraud score?

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a score before authorization, with a response in tens of milliseconds. The scoring path therefore needs a bounded, predictable response time.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency

## Considered Options

* Synchronous scoring API
* Asynchronous scoring

## Decision Outcome

Chosen option: "Synchronous scoring API".

Authorization needs the score before it proceeds, so a synchronous request fits the transaction flow. Its dependency makes availability and latency controls essential.

### Consequences

* Authorization depends on scoring availability.
* The API needs strict latency and timeout limits.

## Pros and Cons of the Options

### Synchronous scoring API

* Good, because Direct authorization flow
* Good, because Simple result handling
* Bad, because Adds authorization-path dependency

### Asynchronous scoring

* Good, because Decouples services
* Good, because Absorbs bursts
* Bad, because Cannot gate current authorization
