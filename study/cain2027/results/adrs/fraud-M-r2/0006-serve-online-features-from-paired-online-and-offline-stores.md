# Serve online features from paired online and offline stores

* System: Card-fraud scoring service

## Context and Problem Statement

The scorer needs quick access to features during authorization, while training and audit reconstruction need durable feature data. The paired-store option covers both access patterns.

## Decision Drivers

* Low-latency features
* Durable training data
* Feature provenance

## Considered Options

* Online/offline feature-store architecture (`v:43.4`)
* Online feature-serving pipeline (`v:43.2`)

## Decision Outcome

Chosen option: "Online/offline feature-store architecture" (`v:43.4`).

Choose paired stores to support low-latency inference and preserve features for training and later reconstruction. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)” support this pattern. The checked point had no warnings but was unattested.

### Consequences

* Define feature freshness and consistency rules.
* Record the feature values or immutable feature references used for each score.

## Pros and Cons of the Options

### Online/offline feature-store architecture

* Good, because Online low-latency access
* Good, because Durable training store
* Bad, because Requires keeping stores aligned
* Sources: `s06_p09`, `s21_p09`

### Online feature-serving pipeline

* Good, because Materializes online features
* Good, because Supports inference access
* Bad, because Durable reuse not explicit
* Sources: `s06_p08`, `s21_p08`
