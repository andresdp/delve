# Process incoming documents in batches

* System: Large-scale document classification

## Context and Problem Statement

The insurer classifies millions of documents daily, with seasonal volume changes and no stated real-time latency requirement.

## Decision Drivers

* Millions daily
* Seasonal volume

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

The brief emphasizes daily volume and seasonal variation without specifying immediate results; batch processing is the checked design point choice (d:15, v:15.1).

### Consequences

* Classification results arrive after each batch completes.
* Capacity must handle seasonal peaks.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Scheduled processing
* Good, because Fits bulk workloads
* Bad, because Results wait for batch
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Continuous processing
* Good, because Low result delay
* Bad, because More operational complexity
* Sources: `d:15`, `v:15.2`
