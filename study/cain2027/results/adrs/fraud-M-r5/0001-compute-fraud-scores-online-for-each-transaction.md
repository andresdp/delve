# Compute fraud scores online for each transaction

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs a score within tens of milliseconds, using current transaction context. Batch scoring cannot provide that response path.

## Decision Drivers

* Tens-of-milliseconds scoring
* Current transaction context

## Considered Options

* Online computation serving (`v:31.5`)
* Precomputed offline serving (`v:31.6`)

## Decision Outcome

Chosen option: "Online computation serving" (`v:31.5`).

Online computation fits per-transaction authorization. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” documents online scoring, while “System Architectures for Personalization and Recommendation” documents precomputed serving, which does not meet the request-time requirement.

### Consequences

* Keep the scoring path and its dependencies within the latency budget.
* Capacity must handle transaction peaks.

## Pros and Cons of the Options

### Online computation serving

* Good, because Uses current request context
* Good, because Supports synchronous scoring
* Bad, because Latency depends on online dependencies
* Bad, because Requires serving capacity
* Sources: `s02_p02`, `s02_p13`, `s04_p05`

### Precomputed offline serving

* Good, because Separates scoring from requests
* Good, because Can prepare results in batches
* Bad, because May be stale
* Bad, because Cannot score unseen transactions
* Sources: `s12_p02`, `s12_p03`, `s19_p08`
