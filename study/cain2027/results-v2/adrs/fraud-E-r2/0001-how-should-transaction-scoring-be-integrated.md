# How should transaction scoring be integrated?

* System: Card-fraud scoring service

## Context and Problem Statement

Every payment needs a score before authorization, so scoring must be called on the transaction path. The design space offers service and in-process integration patterns (d:1).

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability
* Model version traceability

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

Peak availability decides: an independently scalable model service supports transaction surges. This gives up the lower call overhead of in-process scoring.

### Consequences

* Requires a highly available online service.
* Model and application releases can be tracked separately.

## Pros and Cons of the Options

### Model as a service

* Good, because Peak availability: scale service independently
* Good, because Traceability: isolate model releases
* Bad, because Latency: network hop on request path
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because Latency: avoid service network hop
* Bad, because Availability: share application failure domain
* Bad, because Traceability: couple model and app releases
* Sources: `d:1`, `v:1.2`
