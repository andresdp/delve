# Serve classifications through batch prediction

* System: Large-scale document classification

## Context and Problem Statement

The system classifies a large volume of documents and several teams consume the results. The brief does not specify synchronous or low-latency access.

## Decision Drivers

* High volume
* Multiple consumers
* Unspecified latency

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Batch serving aligns with the volume and batch-processing choice, while the brief sets no real-time service level. The checked batch point and real-time rival both have no warnings; the latency tradeoff remains a brief-level unknown.

### Consequences

* Consumers read completed predictions from shared storage.
* Result freshness depends on batch cadence.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Writes results to shared storage
* Good, because Fits batch workload
* Bad, because Results are not immediate
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Real-time result delivery
* Good, because Service interface for consumers
* Bad, because Requires online capacity
* Sources: `d:5`, `v:5.1`
