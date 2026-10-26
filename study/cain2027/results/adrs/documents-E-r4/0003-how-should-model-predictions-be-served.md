# How should model predictions be served?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, and the brief does not require synchronous responses. Scheduled batch serving can write predictions to shared storage for downstream consumers.

## Decision Drivers

* Several consuming teams
* Millions of predictions
* Unspecified response latency

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)
* Hybrid online/offline model serving (`v:5.5`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Batch serving fits the selected processing approach and provides results for multiple consumers without assuming an immediate-response requirement. The checked combination had no warnings and was unattested.

### Consequences

* Consumers need access to the prediction store.
* Freshness depends on the batch schedule.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Writes scheduled prediction batches
* Good, because Supports downstream consumption
* Bad, because Results are not immediate
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Serves predictions in real time
* Good, because Offers a service interface
* Bad, because Requires online serving capacity
* Sources: `d:5`, `v:5.1`

### Hybrid online/offline model serving

* Good, because Supports batch and online use
* Good, because Can serve varied latency needs
* Bad, because Adds serving paths to operate
* Sources: `d:5`, `v:5.5`
