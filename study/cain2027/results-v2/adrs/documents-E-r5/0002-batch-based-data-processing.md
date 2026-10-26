# Batch-based data processing

*Should data be processed in batches or in real time?*

* System: Large-scale document classification

## Context and Problem Statement

The classifier must handle millions of documents daily, with load that varies over the year. No real-time service level is specified.

## Decision Drivers

* High daily volume
* Seasonal volume swings

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

High daily volume and seasonal swings decide in favor of scheduled batch processing. The trade-off is slower result availability, which the brief does not constrain with a latency target.

### Consequences

* Classification results arrive after a processing run.
* Capacity must be planned for seasonal peaks.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Seasonal capacity: schedule processing windows
* Bad, because Freshness: results wait for a batch
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Freshness: process incoming data continuously
* Bad, because Seasonal capacity: ongoing demand as volume changes
* Sources: `d:15`, `v:15.2`
