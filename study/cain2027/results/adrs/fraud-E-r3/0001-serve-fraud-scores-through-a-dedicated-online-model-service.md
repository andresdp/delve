# Serve fraud scores through a dedicated online model service

* System: Card-fraud scoring service

## Context and Problem Statement

Every transaction needs a score before authorization, within tens of milliseconds. The service must handle peak traffic.

## Decision Drivers

* Tens of milliseconds
* Peak availability
* Online authorization

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

The brief requires online scoring and peak resilience; a dedicated model service supports separate scaling and deployment. The checked design point had no warnings, though no sources attested to the full combination.

### Consequences

* Operate a separate scoring service.
* Network latency consumes part of the response budget.

## Pros and Cons of the Options

### Model as a service

* Good, because Separate model service
* Good, because Independent deployment
* Bad, because Network hop
* Bad, because Service operations
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because No service hop
* Good, because Simpler deployment
* Bad, because Tighter coupling
* Bad, because Scaling tied to application
* Sources: `d:1`, `v:1.2`
