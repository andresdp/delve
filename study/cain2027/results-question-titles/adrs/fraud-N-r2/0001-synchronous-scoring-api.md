# Synchronous scoring API

*How should scoring fit into authorization?*

* System: Card-fraud scoring service

## Context and Problem Statement

Every transaction needs a fraud score before authorization, with a response in tens of milliseconds. The scoring path therefore needs a synchronous request and response.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency

## Considered Options

* Synchronous scoring API
* Asynchronous scoring event

## Decision Outcome

Chosen option: "Synchronous scoring API".

Inline scoring meets the requirement to score before authorization and return results within tens of milliseconds.

### Consequences

* Authorization needs a defined scorer timeout policy.
* The scoring API must sustain peak request rates.

## Pros and Cons of the Options

### Synchronous scoring API

* Good, because Score returned inline
* Good, because Simple authorization flow
* Bad, because Authorization depends on scorer
* Bad, because Timeouts need handling

### Asynchronous scoring event

* Good, because Loose coupling
* Good, because Absorbs bursts
* Bad, because Score arrives later
* Bad, because Does not fit inline authorization
