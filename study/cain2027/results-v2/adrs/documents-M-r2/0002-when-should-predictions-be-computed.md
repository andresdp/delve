# When should predictions be computed?

* System: Large-scale document classification

## Context and Problem Statement

The classifier must process millions of documents, and several teams consume its results. The brief sets no per-document response-time target.

## Decision Drivers

* High daily volume
* Multiple consumers
* Seasonal capacity swings

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

High daily volume decides the choice: scheduled scoring can write results for multiple teams to consume, as described in “Architecting a Machine Learning Pipeline” and “System Architectures for Personalization and Recommendation.” This gives up immediate results; the brief provides no latency requirement to justify online serving.

### Consequences

* Teams consume persisted results after each run.
* Run cadence sets result freshness.
* Batch failures can delay results for every consumer.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because High volume: scores large sets in scheduled runs
* Good, because Multiple consumers: writes results to shared storage
* Bad, because Freshness: results wait for a run
* Sources: `s02_p02`, `s12_p02`, `s19_p14`

### Queue-fronted online serving cluster

* Good, because Freshness: scores on demand
* Good, because High volume: queue distributes requests
* Bad, because Cost: serving capacity remains provisioned
* Sources: `s02_p11`, `s12_p07`, `s19_p15`
