# Prediction serving mode

* System: Card-fraud scoring service

## Context and Problem Statement

Each card must be scored before authorization, with tens-of-milliseconds response time. Scheduled batch scoring cannot provide a fresh score for each transaction.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency
* Peak throughput

## Considered Options

* Queue-fronted online serving cluster (`v:31.1`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Queue-fronted online serving cluster" (`v:31.1`).

It supports online scoring and distributes requests across predictors, matching the authorization latency and peak-load drivers. Evidence from “Architecting a Machine Learning Pipeline” and “System Architectures for Personalization and Recommendation” supports the pattern; the checked rival point used batch scoring and was also unattested, so the brief’s per-transaction timing is decisive.

### Consequences

* Keep the synchronous scoring path short.
* Size and operate the queue and predictor pool for peaks.

## Pros and Cons of the Options

### Queue-fronted online serving cluster

* Good, because Online scoring
* Good, because Queue distributes load
* Bad, because Queue adds a latency hop
* Bad, because Requires capacity management
* Sources: `s02_p11`, `s02_p13`, `s12_p07`, `s19_p15`

### Scheduled batch prediction deployment

* Good, because Scores many records together
* Good, because Writes results for later use
* Bad, because Scores are not current per transaction
* Bad, because Does not fit authorization flow
* Sources: `s01_p08`, `s02_p02`, `s02_p12`, `s02_p13`, `s12_p02`, `s15_p04`, `s15_p05`, `s19_p14`, `s19_p16`, `s25_p06`
