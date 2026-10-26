# Should classification processing be batched or real time?

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents daily, but the brief sets no response-time target. The design space frames batch and real-time processing as alternatives (d:15).

## Decision Drivers

* Seasonal peak scale
* Daily throughput

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Seasonal peak scale decides the choice because no latency target requires real-time processing. This gives up prompt per-document results.

### Consequences

* Processing cadence sets result freshness.
* Batch capacity must cover peak periods.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Seasonal peak scale: process accumulated work in scheduled runs
* Bad, because Latency: classification waits for processing
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Latency: process documents continuously
* Bad, because Seasonal peak scale: requires capacity for variable continuous load
* Sources: `d:15`, `v:15.2`
