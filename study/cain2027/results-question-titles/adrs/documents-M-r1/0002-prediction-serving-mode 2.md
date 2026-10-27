# Prediction serving mode

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, with strong seasonal variation, and multiple teams consume classification results. The brief does not specify an interactive latency requirement.

## Decision Drivers

* High daily volume
* Seasonal demand
* Multiple consumers

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)
* Serverless function deployment (`v:31.2`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Choose scheduled batch scoring because the brief describes very high document volume but gives no need for immediate responses; persisted results can serve several teams. “Architecting a Machine Learning Pipeline” and “Three Levels of ML Software” describe batch prediction deployments.

### Consequences

* Agree on result freshness with consuming teams.
* Persist results for downstream access.
* Schedule capacity for seasonal peaks.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Processes large volumes
* Good, because Writes reusable results
* Bad, because Results arrive on a schedule
* Bad, because Peak windows need capacity planning
* Sources: `s02_p02`, `s02_p12`, `s12_p02`, `s19_p14`

### Queue-fronted online serving cluster

* Good, because Distributes request load
* Good, because Supports low latency
* Bad, because More serving infrastructure
* Bad, because Seasonal peaks require scaling
* Sources: `s02_p11`, `s12_p07`, `s19_p15`

### Serverless function deployment

* Good, because Managed scaling
* Good, because Less runtime operations
* Bad, because Runtime limits may constrain workloads
* Bad, because Cost varies with volume
* Sources: `s04_p01`, `s04_p06`, `s11_p04`
