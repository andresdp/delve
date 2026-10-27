# Serve online features from a low-latency feature pipeline

* System: Card-fraud scoring service

## Context and Problem Statement

Online scores depend on current transaction data and engineered features. Feature retrieval is part of the scoring latency budget.

## Decision Drivers

* Low-latency scoring
* Consistent feature inputs

## Considered Options

* Online feature-serving pipeline (`v:43.2`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online feature-serving pipeline" (`v:43.2`).

A low-latency serving store best fits request-time feature access. “Productionizing Machine Learning with a Microservices Architecture” describes shared feature preparation and online serving, while the central analytical platform option does not establish the required serving latency.

### Consequences

* Keep feature generation and model inputs aligned.
* Feature-store availability becomes part of scoring availability.

## Pros and Cons of the Options

### Online feature-serving pipeline

* Good, because Materializes features for online access
* Good, because Shares feature preparation
* Bad, because Requires a serving store
* Bad, because Adds a runtime dependency
* Sources: `s04_p01`, `s04_p04`, `s04_p05`, `s13_p11`

### Central analytical ML data platform

* Good, because Centralizes prepared data
* Good, because Supports downstream reuse
* Bad, because Optimized for analytics
* Bad, because Online latency fit is unspecified
* Sources: `s01_p05`, `s01_p06`, `s09_p08`
