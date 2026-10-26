# Model integration

* System: Card-fraud scoring service

## Context and Problem Statement

Every transaction needs a score before authorization, and auditors need model version and feature lineage. The design space covers integration patterns (d:1).

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability
* Auditability

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)
* Model as module in modular monolith (`v:1.3`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

Peak availability decides: a separate model service can scale independently under load. This gives up the lower latency of an in-process call; the checked design point had no warnings, though no sources attested the combination.

### Consequences

* Network call is on the authorization path.
* Model capacity can scale independently.

## Pros and Cons of the Options

### Model as a service

* Good, because Peak availability: scale model service independently
* Good, because Auditability: isolate model version per service
* Bad, because Low latency: network hop
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because Low latency: direct in-process call
* Bad, because Peak availability: scale application and model together
* Bad, because Auditability: model releases coupled to application
* Sources: `d:1`, `v:1.2`

### Model as module in modular monolith

* Good, because Low latency: in-process module call
* Bad, because Peak availability: scale application and model together
* Sources: `d:1`, `v:1.3`
