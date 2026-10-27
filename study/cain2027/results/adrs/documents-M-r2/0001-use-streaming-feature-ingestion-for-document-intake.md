# Use streaming feature ingestion for document intake

* System: Large-scale document classification

## Context and Problem Statement

Millions of daily documents and strong seasonal volume changes require ingestion that can accommodate changing input rates.

## Decision Drivers

* Millions of documents daily
* Seasonal volume variation

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "Streaming feature ingestion" (`v:21.2`).

Streaming ingestion fits continuous document arrival and variable volume. The design point check found no adopting source for the full combination, so this remains a novel combination rather than an attested one.

### Consequences

* Plan for variable-rate stream processing.
* Retain data needed for training and replay.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because Batch processing
* Good, because Established pipeline pattern
* Bad, because Less suited to continuous intake
* Sources: `s02_p12`, `s04_p04`

### Streaming feature ingestion

* Good, because Continuous intake
* Good, because Event-driven processing
* Bad, because Requires stream operations
* Sources: `s02_p04`, `s04_p11`
