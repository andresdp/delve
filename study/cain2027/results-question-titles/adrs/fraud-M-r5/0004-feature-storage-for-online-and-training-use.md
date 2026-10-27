# Feature storage for online and training use

* System: Card-fraud scoring service

## Context and Problem Statement

Online scores need quickly retrievable features, while audit and reproducibility require retaining the inputs associated with scoring and model versions.

## Decision Drivers

* Low-latency feature access
* Training and reuse
* Auditable scoring inputs

## Considered Options

* Online/offline feature-store architecture (`v:43.4`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online/offline feature-store architecture" (`v:43.4`).

Choose complementary online and durable stores to serve inference features quickly while retaining data for training and reuse. “MLOps: Continuous delivery and automation pipelines in machine learning” supports this pattern; the brief’s latency and audit requirements favor it over an analytical platform alone.

### Consequences

* Online and offline feature values need consistency checks.
* Feature lineage must connect scoring inputs to model versions.

## Pros and Cons of the Options

### Online/offline feature-store architecture

* Good, because Fast online feature reads
* Good, because Durable store supports reuse
* Bad, because Requires two coordinated stores
* Bad, because Feature consistency needs care
* Sources: `s06_p09`, `s21_p09`

### Central analytical ML data platform

* Good, because Shared analytical platform
* Good, because Supports downstream pipelines
* Bad, because Online latency fit is unclear
* Bad, because May require serving materialization
