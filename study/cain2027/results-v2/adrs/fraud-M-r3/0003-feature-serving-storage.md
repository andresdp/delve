# Feature serving storage

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring needs features available within tens of milliseconds, while later audits require the feature values associated with a score to remain available. Serving and durable storage must support both needs.

## Decision Drivers

* Latency: tens of milliseconds
* Auditability: feature traceability

## Considered Options

* Online/offline feature-store architecture (`v:43.4`)
* Online feature-serving pipeline (`v:43.2`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online/offline feature-store architecture" (`v:43.4`).

The latency deadline and need to retain features both decide this choice: complementary online and durable stores address the two access patterns. We accept the operational cost of keeping the stores aligned; “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)” describe this architecture.

### Consequences

* Maintain online and durable feature representations.
* Record the feature values used for each scored transaction.

## Pros and Cons of the Options

### Online/offline feature-store architecture

* Good, because Latency: online store supports fast inference reads
* Good, because Auditability: durable store retains features
* Bad, because Availability: requires keeping complementary stores aligned
* Sources: `s06_p09`, `s21_p09`

### Online feature-serving pipeline

* Good, because Latency: materializes features for online inference
* Good, because Availability: shared preparation pipeline
* Bad, because Auditability: durable feature history is not explicit
* Sources: `s06_p09`

### Central analytical ML data platform

* Good, because Auditability: centralizes prepared data
* Good, because Availability: supports downstream ML pipelines
* Bad, because Latency: analytical storage may not serve tight online reads
* Sources: `s01_p05`, `s01_p06`, `s09_p08`
