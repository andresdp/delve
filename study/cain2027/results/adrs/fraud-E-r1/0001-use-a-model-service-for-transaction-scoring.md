# Use a model service for transaction scoring

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a fraud score before authorization, within tens of milliseconds.

## Decision Drivers

* Online scoring
* Low latency
* Peak availability

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

A dedicated service fits online scoring and isolates the model behind a serving boundary (d:1, v:1.1).

### Consequences

* The scoring service needs capacity for traffic peaks.
* Service latency must fit the authorization path.

## Pros and Cons of the Options

### Model as a service

* Good, because Separate model service
* Good, because Supports online integration
* Bad, because Adds a service boundary
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because Direct application integration
* Bad, because Tighter application coupling
* Sources: `d:1`, `v:1.2`
