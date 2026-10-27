# Use batch ETL for weekly labelled-image ingestion

* System: On-device visual inspection

## Context and Problem Statement

New labels arrive for weekly retraining, and the brief does not require live data ingestion.

## Decision Drivers

* Weekly retraining
* Limited infrastructure budget

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "ETL-based feature ingestion" (`v:21.1`).

Weekly retraining favors a batch path. The source “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” documents ETL-based ingestion.

### Consequences

* Images and labels are collected into batches before training.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because Fits batch workflow
* Good, because Supported by sources
* Bad, because No live ingestion
* Sources: `s02_p12`, `s04_p04`

### Streaming feature ingestion

* Good, because Continuous data flow
* Bad, because More operational overhead
