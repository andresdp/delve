# Model integration

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs a synchronous score within tens of milliseconds. The model must fit a request path that can keep serving through peak load.

## Decision Drivers

* Tens of milliseconds
* Peak availability

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

Choose a separately deployable model service to scale the scoring tier for peaks; validate the added network hop against the latency budget. (d:1, v:1.1)

### Consequences

* Operate model service availability and capacity.
* Measure end-to-end scoring latency.

## Pros and Cons of the Options

### Model as a service

* Good, because Independent scaling
* Good, because Separate deployment
* Bad, because Network hop
* Bad, because Service dependency
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because No model service hop
* Good, because Simple request path
* Bad, because Coupled deployments
* Bad, because Shared scaling
* Sources: `d:1`, `v:1.2`
