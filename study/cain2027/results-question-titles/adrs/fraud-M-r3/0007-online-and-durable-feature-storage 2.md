# Online and durable feature storage

* System: Card-fraud scoring service

## Context and Problem Statement

Online scoring needs quick feature access, while later audits need the feature values that contributed to each score.

## Decision Drivers

* Low-latency feature reads
* Feature audit trail
* Durable retention

## Considered Options

* Online/offline feature-store architecture (`v:43.4`)
* Online feature-serving pipeline (`v:43.2`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online/offline feature-store architecture" (`v:43.4`).

Complementary stores address fast inference reads and durable feature retention. Google’s “MLOps: Continuous delivery and automation pipelines in machine learning” describes an online/offline feature-store architecture.

### Consequences

* Keep feature transformations consistent across stores.
* Record the exact feature values or immutable references used per score.

## Pros and Cons of the Options

### Online/offline feature-store architecture

* Good, because Separates fast and durable access
* Good, because Supports reuse
* Bad, because Requires consistency between stores
* Sources: `s06_p09`, `s21_p09`

### Online feature-serving pipeline

* Good, because Materializes features for inference
* Good, because Supports low-latency reads
* Bad, because Durable audit needs are less explicit

### Central analytical ML data platform

* Good, because Shared prepared data platform
* Good, because Supports downstream workflows
* Bad, because Online latency fit is unclear
