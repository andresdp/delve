# Ingest labelled images in batches

* System: On-device visual inspection

## Context and Problem Statement

The brief describes newly labelled images used for weekly retraining, rather than a requirement to train continuously as images arrive.

## Decision Drivers

* Weekly retraining
* New labelled images

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion matches the stated retraining cadence and avoids adding streaming operations without a stated need (d:7, v:7.3).

### Consequences

* Images become available to training at batch boundaries.
* Define a reliable batch handoff from labelling.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Fits weekly cadence
* Good, because Simple processing
* Bad, because Updates wait for batch
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous arrival
* Bad, because More operational complexity
* Sources: `d:7`, `v:7.1`
