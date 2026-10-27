# Online feature serving

* System: Card-fraud scoring service

## Context and Problem Statement

Online scoring needs the transaction’s current context and low-latency access to prepared features. A shared preparation pipeline can materialize those features for inference.

## Decision Drivers

* Fresh transaction context
* Low-latency feature access
* Training and serving consistency

## Considered Options

* Online feature-serving pipeline (`v:43.2`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online feature-serving pipeline" (`v:43.2`).

The online feature pipeline explicitly materializes features in a low-latency serving store, which fits scoring before authorization. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps Principles” support this pattern.

### Consequences

* Operate the online feature store on the latency-critical path.
* Keep feature preparation aligned with model inputs.

## Pros and Cons of the Options

### Online feature-serving pipeline

* Good, because Features prepared for online access
* Good, because Shared preparation pipeline
* Bad, because Requires online store operations
* Bad, because Feature freshness must be maintained
* Sources: `s04_p01`, `s04_p04`, `s04_p05`, `s04_p11`, `s13_p11`, `s20_p06`, `s22_p03`, `s22_p17`

### Central analytical ML data platform

* Good, because Shared prepared data
* Good, because Supports downstream workflows
* Bad, because Analytical storage may not meet serving latency
* Bad, because No explicit online serving store
