# How should classification predictions be served?

* System: Large-scale document classification

## Context and Problem Statement

Millions of incoming documents arrive daily, with strong seasonal volume swings; several teams consume the results.

## Decision Drivers

* Variable high volume
* Shared results
* Cost efficiency

## Considered Options

* Hybrid online/offline model serving (`v:5.5`)
* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Hybrid online/offline model serving" (`v:5.5`).

Variable seasonal volume decides the choice: batch processing can absorb bulk work while an online path supports time-sensitive requests. This costs more operational effort than one serving path.

### Consequences

* Operate and monitor online and batch paths.
* Define how consumers retrieve results from either path.

## Pros and Cons of the Options

### Hybrid online/offline model serving

* Good, because Variable volume: route work between online and batch paths
* Good, because Cost efficiency: batch work can reduce per-item overhead
* Bad, because Operational simplicity: two serving paths to maintain
* Sources: `d:5`, `v:5.5`

### Data batch based model serving

* Good, because Cost efficiency: scheduled batches suit high volume
* Bad, because Timeliness: results wait for batch runs
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Timeliness: results available through a real-time service
* Bad, because Variable volume: capacity must handle peak demand
* Bad, because Cost efficiency: always-ready service capacity
* Sources: `d:5`, `v:5.1`
