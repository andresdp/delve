# Model as a service

*How to integrate the model?*

* System: Card-fraud scoring service

## Context and Problem Statement

The service must score transactions synchronously before authorization. Its integration pattern affects serving latency and scaling (d:1, d:5).

## Decision Drivers

* tens of milliseconds
* peak availability

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

A dedicated service gives the scoring path an independent deployment and scaling boundary; the brief’s latency requirement makes service performance testing essential (d:1, d:5, d:26).

### Consequences

* Operate a highly available scoring service.
* Measure end-to-end latency under peak load.

## Pros and Cons of the Options

### Model as a service

* Good, because Independent scaling
* Good, because Clear model boundary
* Bad, because Network hop
* Bad, because Service operations
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because No service hop
* Good, because Simple deployment
* Bad, because Coupled release
* Bad, because Shared scaling
* Sources: `d:1`, `v:1.2`
