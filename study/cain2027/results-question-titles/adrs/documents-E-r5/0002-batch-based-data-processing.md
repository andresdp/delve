# Batch-based data processing

*Should documents be processed in batches or in real time?*

* System: Large-scale document classification

## Context and Problem Statement

The system must classify millions of documents per day, but the brief does not specify response-time targets. Batch processing is the checked design choice for handling the stated workload.

## Decision Drivers

* high volume
* seasonal variation
* unspecified latency

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

The brief emphasizes scale and seasonal variation without requiring real-time results, so batch processing is a reasonable fit. The checked point had no warnings and no attesting sources.

### Consequences

* Choose processing windows and backlog targets.
* Plan capacity for seasonal peaks.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because processes grouped workloads
* Good, because supports scheduled capacity
* Bad, because classification is delayed
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because processes as documents arrive
* Good, because reduces processing delay
* Bad, because requires streaming operations
* Sources: `d:15`, `v:15.2`
