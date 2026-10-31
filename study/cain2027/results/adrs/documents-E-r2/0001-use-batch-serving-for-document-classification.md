# Use batch serving for document classification

* System: Large-scale document classification

## Context and Problem Statement

The insurer processes millions of documents daily, and demand varies seasonally. The brief does not require immediate predictions.

## Decision Drivers

* High daily volume
* Seasonal demand
* Multiple consumers

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Batch serving aligns with high-volume document classification and leaves capacity to scale scheduled processing for seasonal peaks. The checked batch point was novel and unattested; the real-time rival was also novel and unattested (d:5, d:15).

### Consequences

* Consumers read completed predictions from storage.
* Classification latency depends on batch schedule.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Scheduled bulk processing
* Good, because Writes results to storage
* Bad, because Results arrive after each batch
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Real-time predictions
* Good, because Distributed service
* Bad, because Per-request serving path
* Sources: `d:5`, `v:5.1`
