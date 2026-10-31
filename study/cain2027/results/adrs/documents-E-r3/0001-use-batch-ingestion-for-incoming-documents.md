# Use batch ingestion for incoming documents

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents each day, and volume varies strongly over the year. The design space includes batch and streamed ingestion (d:7).

## Decision Drivers

* High daily volume
* Seasonal volume variation

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion fits the stated scale and allows processing capacity to follow seasonal volume. The checked design point had no warnings, though it was unattested.

### Consequences

* Classification runs on collected batches.
* Batch timing and size need operational definition.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Groups high-volume input
* Good, because Fits offline processing
* Bad, because Results arrive after batch processing
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous input
* Good, because Supports prompt processing
* Bad, because Requires stream handling
* Sources: `d:7`, `v:7.1`
