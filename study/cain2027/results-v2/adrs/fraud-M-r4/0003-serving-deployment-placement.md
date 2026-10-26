# Serving deployment placement

* System: Card-fraud scoring service

## Context and Problem Statement

The model must score live transactions as part of authorization. The system therefore needs a production runtime that can expose real-time predictions.

## Decision Drivers

* Tens-of-milliseconds scoring
* Peak availability

## Considered Options

* Model-as-a-service deployment (`v:30.3`)
* Monolithic application architecture (`v:30.2`)
* Containerized offline prediction service (`v:30.1`)

## Decision Outcome

Chosen option: "Model-as-a-service deployment" (`v:30.3`).

Peak availability decides in favor of an independently deployable prediction service that can scale with demand. It adds a service boundary, so latency must be measured across the full authorization path.

### Consequences

* Deploy and operate the model service alongside the authorization system.
* Keep the service call within the scoring latency budget.

## Pros and Cons of the Options

### Model-as-a-service deployment

* Good, because Low latency: real-time prediction service
* Good, because Peak availability: service can scale independently
* Bad, because Latency: adds a service boundary
* Sources: `s01_p06`, `s04_p01`

### Monolithic application architecture

* Good, because Low latency: avoids a separate model service call
* Bad, because Peak availability: model and application scale together

### Containerized offline prediction service

* Good, because Availability: isolated runtime
* Bad, because Low latency: offline scoring misses live authorization
