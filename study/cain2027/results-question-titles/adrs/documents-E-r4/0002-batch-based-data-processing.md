# Batch-based data processing

*Should documents be processed in batches or in real time?*

* System: Large-scale document classification

## Context and Problem Statement

The classifier must handle millions of documents each day, but the brief gives no latency target. Batch processing aligns with bulk volume; real-time processing remains an option if consumers need immediate results.

## Decision Drivers

* High throughput
* Seasonal scaling
* Unspecified latency

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Without a stated latency requirement, batch processing is a reasonable fit for the stated daily scale and seasonal variation. The rival real-time combination also produced no design-space warnings; neither combination is attested.

### Consequences

* Consumers receive results after batch processing.
* A latency requirement could change this choice.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Processes bulk workloads
* Good, because Can schedule around demand
* Bad, because Adds processing delay
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes arrivals continuously
* Good, because Can reduce result delay
* Bad, because Needs continuous stream capacity
* Sources: `d:15`, `v:15.2`
