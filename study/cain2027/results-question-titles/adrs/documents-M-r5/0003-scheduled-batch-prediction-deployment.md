# Scheduled batch prediction deployment

*When should predictions be computed?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, and the brief sets no per-document response-time requirement. Scheduled batch scoring can write results for downstream use.

## Decision Drivers

* Millions of documents daily
* Several consuming teams

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Choose batch scoring because the brief emphasizes volume and shared results, without requiring immediate responses. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Three Levels of ML Software” describe scheduled batch deployment; the rival online option is supported by “System Architectures for Personalization and Recommendation.”

### Consequences

* Agree result delivery cadence with consuming teams.
* Persist results for downstream access and review.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Processes large workloads in batches
* Good, because Writes results for later consumption
* Bad, because Results are not immediate
* Bad, because Batch timing must meet consumer needs
* Sources: `s02_p02`, `s02_p12`, `s15_p04`

### Queue-fronted online serving cluster

* Good, because Supports low-latency requests
* Good, because Queue helps distribute load
* Bad, because Adds always-ready serving capacity
* Bad, because Online latency needs are unspecified
* Sources: `s02_p11`, `s12_p07`
