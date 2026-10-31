# Use a model service for transaction scoring

* System: Card-fraud scoring service

## Context and Problem Statement

Every transaction needs a fraud score before authorization, with a response in tens of milliseconds. The model must be independently identifiable for later audit.

## Decision Drivers

* Low-latency scoring
* Model traceability

## Considered Options

* Model as a service (`v:1.1`)
* Model as module in modular monolith (`v:1.3`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

A dedicated model service provides a clear unit to version and identify for each score. The brief’s latency target makes synchronous real-time service operation necessary.

### Consequences

* Keep service calls on the authorization path.
* Record the serving model version with each score.

## Pros and Cons of the Options

### Model as a service

* Good, because Separate model boundary
* Good, because Clear model identity
* Bad, because Network hop
* Bad, because Service operations
* Sources: `d:1`, `v:1.1`

### Model as module in modular monolith

* Good, because In-process call
* Good, because Fewer services
* Bad, because Shared release boundary
* Bad, because Tighter coupling
* Sources: `d:1`, `v:1.3`
