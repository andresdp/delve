# Model integration

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization path needs a real-time score. The integration choice affects serving and must support traceability to the model used.

## Decision Drivers

* Tens-of-milliseconds latency
* Synchronous scoring
* Model identification

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)
* Model as module in modular monolith (`v:1.3`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

A dedicated service gives the model an independent versioned boundary for scoring and audit records. Its network cost needs to be measured against the latency budget.

### Consequences

* Record the serving model version with each score.
* Keep the synchronous call path short.

## Pros and Cons of the Options

### Model as a service

* Good, because Independent model deployment
* Good, because Clear model boundary
* Bad, because Network hop
* Bad, because Service dependency
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because Fewer network calls
* Good, because Simple request path
* Bad, because Tied application releases
* Bad, because Shared scaling
* Sources: `d:1`, `v:1.2`

### Model as module in modular monolith

* Good, because Local execution
* Good, because Separate module boundary
* Bad, because Shared deployment
* Bad, because Shared scaling
* Sources: `d:1`, `v:1.3`
