# Serve scores synchronously for authorization

* System: Card-fraud scoring service

## Context and Problem Statement

The service must return a fraud score within tens of milliseconds. Main requirements, in priority order: low scoring latency; continued operation during peak load; auditability of the model version and features used.

## Decision Drivers

* Tens-of-milliseconds latency
* Peak-load availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Peak-load availability decides in favor of independently scalable serving; it adds a network hop, so the service must be capacity-tested against the latency target.

### Consequences

* Requires network calls on the authorization path.
* Requires independent capacity management.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Peak-load availability: scale service independently
* Bad, because Latency: adds a network boundary
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Latency: local scoring path
* Bad, because Peak-load availability: scales with host capacity
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Peak-load availability: schedule batch capacity
* Bad, because Latency: scores are not synchronous
* Sources: `d:5`, `v:5.3`
