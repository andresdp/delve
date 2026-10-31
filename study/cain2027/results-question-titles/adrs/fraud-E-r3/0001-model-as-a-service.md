# Model as a service

*How should the scoring model integrate with the payments application?*

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a score before authorization. A separately deployable model service fits the online scoring path.

## Decision Drivers

* score before authorization
* peak availability

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

A dedicated service can scale for transaction peaks and isolates model deployment; the extra network hop must fit the latency budget. (d:1, v:1.1)

### Consequences

* Keep the synchronous service path low latency.
* Scale and monitor the scoring service independently.

## Pros and Cons of the Options

### Model as a service

* Good, because independent scaling
* Good, because separate deployment
* Bad, because network hop
* Bad, because service dependency
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because no remote call
* Good, because simple request path
* Bad, because coupled deployment
* Bad, because shared scaling limits
* Sources: `d:1`, `v:1.2`
