# Publish predictions through batch serving

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, and the brief does not require synchronous predictions.

## Decision Drivers

* Multiple consumers
* Millions daily

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Scheduled prediction batches fit the processing choice and give multiple teams a shared result set; this choice was included in the checked point (d:5, v:5.3).

### Consequences

* Consumers need access to persisted results.
* Result availability follows batch completion.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Writes results to shared storage
* Good, because Fits batch workflow
* Bad, because Consumers wait for output
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Real-time predictions
* Good, because Service interface
* Bad, because Requires online capacity
* Sources: `d:5`, `v:5.1`
