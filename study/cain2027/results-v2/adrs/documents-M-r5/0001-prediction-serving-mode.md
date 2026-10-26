# Prediction serving mode

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, and volume varies sharply by season. The brief sets no request-latency or freshness target.

## Decision Drivers

* Seasonal volume
* Serving cost
* Multiple consumers

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Seasonal volume and serving cost decide the choice: scheduled scoring handles large, variable workloads without requiring an online response path. This gives up immediate predictions; the design point is novel and unattested, and sources including “Architecting a Machine Learning Pipeline” and “Three Levels of ML Software” describe batch deployment patterns.

### Consequences

* Consumers retrieve completed results from shared storage.
* Classification freshness depends on the scoring schedule.
* Plan capacity for seasonal peaks.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Seasonal volume: score large queues in scheduled runs
* Good, because Serving cost: write results for consumers to retrieve
* Bad, because Freshness: results wait for the next run
* Bad, because Multiple consumers: requires shared result storage
* Sources: `s02_p02`, `s02_p12`, `s02_p13`, `s12_p02`, `s15_p04`, `s15_p05`, `s19_p14`, `s19_p16`, `s25_p06`

### Online computation serving

* Good, because Freshness: scores current requests
* Good, because Multiple consumers: supports request-based integration
* Bad, because Seasonal volume: must handle peak request load
* Bad, because Serving cost: keeps prediction capacity available for requests
* Sources: `s02_p02`, `s02_p13`, `s04_p10`, `s05_p02`, `s11_p07`, `s12_p02`, `s12_p03`, `s12_p04`, `s12_p07`, `s15_p04`, `s15_p05`, `s19_p08`, `s19_p13`, `s24_p01`, `s24_p05`
