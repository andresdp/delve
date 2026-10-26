# Process documents in batches or in real time?

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents daily, with volume varying by season. The brief gives no per-document latency target.

## Decision Drivers

* Millions of documents/day
* Seasonal volume

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Seasonal scale and daily volume decide the choice because the brief sets no latency target; results may take longer while a batch runs.

### Consequences

* Schedule batches to meet downstream needs.
* Adjust capacity for seasonal peaks.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Throughput: process large volumes together
* Good, because Cost: scale capacity with workload
* Bad, because Latency: results wait for a batch
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Latency: process documents as they arrive
* Bad, because Cost: continuous processing capacity
* Sources: `d:15`, `v:15.2`
