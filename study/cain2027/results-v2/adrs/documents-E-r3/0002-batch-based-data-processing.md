# Batch-based data processing

*How should incoming documents be processed?*

* System: Large-scale document classification

## Context and Problem Statement

The system must ingest millions of documents per day, and volume changes considerably by season.

## Decision Drivers

* High throughput
* Variable volume
* Cost efficiency

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Cost efficiency and seasonal volume decide the choice: batch processing can group the large workload and adjust run capacity. The trade-off is that some classifications wait for the next batch.

### Consequences

* Set batch size and processing cadence to meet business timeliness needs.
* Scale batch capacity for seasonal peaks.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Cost efficiency: group work into batches
* Good, because Variable volume: schedule capacity around demand
* Bad, because Timeliness: results may wait for a batch window
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Timeliness: process arrivals continuously
* Bad, because Cost efficiency: maintain continuous processing capacity
* Sources: `d:15`, `v:15.2`
