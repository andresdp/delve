# Deploy the model as a real-time service

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores are required before each card transaction is authorized, so batch prediction cannot serve the primary path. A real-time model service fits that interaction.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Model-as-a-service deployment (`v:30.3`)
* Containerized offline prediction service (`v:30.1`)

## Decision Outcome

Chosen option: "Model-as-a-service deployment" (`v:30.3`).

The brief requires an online score before authorization; a real-time service directly meets that need. Sources describe this deployment as serving predictions to product applications.

### Consequences

* Keep model instances warm for request latency.
* Operate and scale the scoring service.

## Pros and Cons of the Options

### Model-as-a-service deployment

* Good, because Real-time predictions
* Good, because Independent model deployment
* Bad, because Service operations required
* Sources: `s01_p06`, `s04_p01`, `s06_p13`

### Containerized offline prediction service

* Good, because Containerized runtime
* Good, because Fits scheduled scoring
* Bad, because Does not fit per-transaction scoring
