# Use a dedicated model service for transaction scoring

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a fraud score before authorization, with a response time of tens of milliseconds. A dedicated service gives the scoring model an online application interface. (d:1)

## Decision Drivers

* Tens of milliseconds
* Pre-authorization scoring

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

A dedicated service supports an online scoring path and provides an independent scaling boundary for transaction peaks. The point check returned no warnings, though it was unattested. (d:1, v:1.1)

### Consequences

* The authorization path depends on service availability.
* Model deployment and service capacity need coordination.

## Pros and Cons of the Options

### Model as a service

* Good, because Dedicated serving boundary
* Good, because Online integration
* Bad, because Network hop
* Bad, because Service operations
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because No service call
* Good, because Simple deployment
* Bad, because Tighter application coupling
* Bad, because Scaling tied to application
* Sources: `d:1`, `v:1.2`
