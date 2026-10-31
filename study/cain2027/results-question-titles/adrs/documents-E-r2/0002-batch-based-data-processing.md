# Batch-based data processing

*Should documents be processed in batches or in real time?*

* System: Large-scale document classification

## Context and Problem Statement

The daily volume is large and varies over the year, while the brief gives no real-time response requirement.

## Decision Drivers

* millions per day
* seasonal variation

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Batch processing matches the stated scale and avoids assuming a latency target the brief does not specify. The checked point had no warnings and no source-attested systems.

### Consequences

* Capacity must scale for peak batches.
* Consumers receive results after each processing run.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because groups high volume
* Good, because supports scheduled capacity
* Bad, because adds processing delay
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because continuous processing
* Good, because faster results
* Bad, because more operational complexity
* Sources: `d:15`, `v:15.2`
