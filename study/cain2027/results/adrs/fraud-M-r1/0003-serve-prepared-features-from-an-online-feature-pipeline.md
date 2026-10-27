# Serve prepared features from an online feature pipeline

* System: Card-fraud scoring service

## Context and Problem Statement

Online scoring needs transaction features available quickly; the brief does not specify how those features are stored or retrieved.

## Decision Drivers

* Low-latency feature access
* Consistent preparation

## Considered Options

* Online feature-serving pipeline (`v:43.2`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online feature-serving pipeline" (`v:43.2`).

Materialized features in a low-latency store fit the synchronous scoring constraint. “Productionizing Machine Learning with a Microservices Architecture” describes a shared preparation pipeline and online feature serving.

### Consequences

* Feature freshness and serving availability need monitoring.
* Feature preparation must be aligned with model inputs.

## Pros and Cons of the Options

### Online feature-serving pipeline

* Good, because Materializes features for inference
* Good, because Shares preparation pipeline
* Bad, because Requires serving-store operations
* Sources: `s04_p01`, `s04_p04`, `s04_p05`, `s22_p03`

### Central analytical ML data platform

* Good, because Shared analytical platform
* Good, because Supports downstream workflows
* Bad, because Does not specify low-latency serving
* Sources: `s22_p03`
