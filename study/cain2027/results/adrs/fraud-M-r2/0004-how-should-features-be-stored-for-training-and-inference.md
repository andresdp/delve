# How should features be stored for training and inference?

* System: Card-fraud scoring service

## Context and Problem Statement

Online scoring needs low-latency feature access, while audit and model development need durable feature data. A single store may not serve both access patterns well.

## Decision Drivers

* Low-latency feature lookup
* Durable training data
* Feature reuse

## Considered Options

* Online/offline feature-store architecture (`v:43.4`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online/offline feature-store architecture" (`v:43.4`).

Separate online and durable stores fit the latency needs of serving while retaining data for training and review. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps: What It Is, Why it Matters, and How To Implement It” describe this arrangement.

### Consequences

* Maintain consistent feature definitions across both stores.
* Manage retention and access controls for durable feature data.

## Pros and Cons of the Options

### Online/offline feature-store architecture

* Good, because Fast online reads
* Good, because Durable offline features
* Bad, because Stores must stay consistent
* Sources: `s06_p09`, `s21_p09`

### Central analytical ML data platform

* Good, because Shared prepared data
* Good, because Supports downstream workflows
* Bad, because Analytical access may not fit online latency
* Sources: `s06_p09`
