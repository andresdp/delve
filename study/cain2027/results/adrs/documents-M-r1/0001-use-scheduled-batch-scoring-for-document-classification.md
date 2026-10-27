# Use scheduled batch scoring for document classification

* System: Large-scale document classification

## Context and Problem Statement

The system processes millions of documents daily, with seasonal volume changes. The brief does not require immediate predictions for each incoming document.

## Decision Drivers

* High daily volume
* Seasonal peaks
* Result delivery to teams

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Batch scoring fits the stated high volume without an unstated real-time requirement. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Three Levels of ML Software” describe scheduled batch prediction deployment.

### Consequences

* Choose a scoring cadence that meets operational freshness needs.
* Persist results where consuming teams can access them.
* Plan capacity for seasonal processing peaks.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Handles bulk scoring
* Good, because Writes results for consumers
* Bad, because Results arrive on a schedule
* Bad, because Freshness depends on cadence
* Sources: `s02_p02`, `s19_p14`

### Queue-fronted online serving cluster

* Good, because Supports low latency
* Good, because Distributes request load
* Bad, because Adds always-on service capacity
* Bad, because Requires online request handling
* Sources: `s02_p11`, `s12_p07`
