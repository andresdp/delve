# Use a model service for transaction scoring

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a fraud score before authorization, within tens of milliseconds. The model must be reachable from the payment application at request time.

## Decision Drivers

* Tens of milliseconds
* Pre-authorization scoring

## Considered Options

* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)
* Model in batch prediction system (`v:1.4`)

## Decision Outcome

Chosen option: "Model as a service" (`v:1.1`).

A request-time model service supports live scoring and keeps model serving separately deployable. The design point had no warnings; the batch rival conflicts with the brief’s timing requirement.

### Consequences

* Keep the scoring call within the latency budget.
* Provide service capacity for peak transaction volume.

## Pros and Cons of the Options

### Model as a service

* Good, because Request-time access
* Good, because Separate model service
* Bad, because Network call overhead
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because Avoids service hop
* Bad, because Tighter application coupling
* Sources: `d:1`, `v:1.2`

### Model in batch prediction system

* Good, because External prediction system
* Bad, because Batch oriented
* Sources: `d:1`, `v:1.4`
