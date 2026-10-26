# How should transaction scores be served?

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a fraud score before authorization, within tens of milliseconds. The serving path must also keep working during demand peaks.

## Decision Drivers

* Tens-of-ms latency
* Peak availability
* Before authorization

## Considered Options

* Queue-fronted online serving cluster (`v:31.1`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Queue-fronted online serving cluster" (`v:31.1`).

Online scoring fits the authorization path, and a queue-fronted cluster is described as supporting load balancing and low latency. Practitioner sources include “Architecting a Machine Learning Pipeline” and “Three Levels of ML Software”; the batch alternative does not fit per-transaction scoring before authorization.

### Consequences

* Keep predictors available for online requests.
* Operate the queue and predictor capacity through peaks.

## Pros and Cons of the Options

### Queue-fronted online serving cluster

* Good, because Online scoring
* Good, because Load balancing
* Good, because Low latency
* Bad, because Queue adds a component
* Bad, because Requires capacity management
* Sources: `s02_p11`, `s02_p13`, `s12_p07`, `s19_p15`

### Scheduled batch prediction deployment

* Good, because Scores computed in advance
* Good, because Simple result delivery
* Bad, because Cannot score each live transaction
* Bad, because Results may be stale
* Sources: `s01_p08`, `s02_p02`, `s02_p12`, `s02_p13`, `s12_p02`, `s15_p04`, `s15_p05`, `s19_p14`, `s19_p16`, `s25_p06`
