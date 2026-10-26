# How to serve classification results

* System: Large-scale document classification

## Context and Problem Statement

Classification results must be made available to several teams, and the brief does not specify a per-document latency target.

## Decision Drivers

* High throughput at scale
* Elasticity across seasonal peaks
* Share results across teams

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)
* Hybrid online/offline model serving (`v:5.5`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Throughput decides: batch serving fits the stated high volume and avoids assuming a real-time requirement. The trade-off is that consumers receive results on the batch schedule.

### Consequences

* Consumers read results from shared storage.
* Result freshness depends on batch cadence.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Throughput: scheduled bulk processing
* Bad, because Availability: results wait for a batch
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Availability: results served in real time
* Bad, because Elasticity: always-on service capacity
* Sources: `d:5`, `v:5.1`

### Hybrid online/offline model serving

* Good, because Flexibility: supports online and batch results
* Bad, because Cost: two serving paths to operate
* Sources: `d:5`, `v:5.5`
