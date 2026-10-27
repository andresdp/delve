# Use scheduled batch prediction for document classification

* System: Large-scale document classification

## Context and Problem Statement

The classifier processes millions of documents daily, with seasonal volume swings. The brief gives no requirement for immediate results.

## Decision Drivers

* Millions of documents daily
* Seasonal volume variation

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Batch scoring fits the stated high volume and avoids assuming a real-time response requirement. The rival online cluster is a viable option if consumers later require immediate classifications, but the brief does not establish that need.

### Consequences

* Consumers receive results after each scheduled run.
* Batch cadence and result availability targets need definition.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Processes large volumes
* Good, because Writes results for consumers
* Bad, because Results wait for batch completion
* Sources: `s02_p02`, `s12_p02`, `s19_p14`

### Queue-fronted online serving cluster

* Good, because Handles requests continuously
* Good, because Queue supports load balancing
* Bad, because Adds serving infrastructure
* Sources: `s02_p11`, `s12_p07`, `s19_p15`
