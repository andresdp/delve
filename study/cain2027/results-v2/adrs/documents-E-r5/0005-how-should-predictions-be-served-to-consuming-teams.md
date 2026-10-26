# How should predictions be served to consuming teams?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, while the brief does not specify synchronous access or a latency requirement. Batch results in shared storage provide a simple fit for scheduled processing and multiple consumers.

## Decision Drivers

* Multiple consuming teams
* High daily volume

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)
* Hybrid online/offline model serving (`v:5.5`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

High daily volume and the absence of a stated real-time requirement decide in favor of batch serving. This gives up immediate results and assumes teams can consume published batches.

### Consequences

* Results are written to storage for team consumption.
* Consumers must handle batch availability and timing.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because High daily volume: process and publish batches
* Bad, because Multiple consuming teams: consumers wait for batch output
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Multiple consuming teams: distributed real-time access
* Bad, because High daily volume: online serving capacity required
* Sources: `d:5`, `v:5.1`

### Hybrid online/offline model serving

* Good, because Multiple consuming teams: supports online and batch consumers
* Bad, because High daily volume: operates two serving paths
* Sources: `d:5`, `v:5.5`
