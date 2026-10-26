# How should predictions be served?

* System: Large-scale document classification

## Context and Problem Statement

The system must classify high volumes and share results with several teams. The brief does not say that every result must be available in real time.

## Decision Drivers

* High volume
* Multiple consumers
* Seasonal volume

## Considered Options

* Data batch based model serving (`v:5.3`)
* Hybrid online/offline model serving (`v:5.5`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Hybrid online/offline model serving" (`v:5.5`).

The hybrid option leaves room for bulk processing while allowing a real-time path if a consuming team needs it. The rival design point that uses only real-time processing is valid but not established as necessary by the brief. The checked combination is novel (`attested_by` is empty).

### Consequences

* Operating both paths adds complexity.
* Batch processing remains the default until latency needs are known.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Scheduled bulk processing
* Good, because Writes results to storage
* Bad, because Results arrive after each batch
* Sources: `d:5`, `v:5.3`

### Hybrid online/offline model serving

* Good, because Supports batch and online paths
* Good, because Can serve differing needs
* Bad, because More serving paths to operate
* Sources: `d:5`, `v:5.5`

### Microservice based model serving

* Good, because Real-time distributed serving
* Good, because Direct access to predictions
* Bad, because Requires peak service capacity
* Sources: `d:5`, `v:5.1`
