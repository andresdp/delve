# Ingest weekly inputs in batches

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts weekly demand, and workflow coordination in the design space requires an ingestion mechanism to be decided first. Batch ETL is a supported option for extracting and transforming records into features.

## Decision Drivers

* Weekly run stability
* Past-week reproducibility

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "ETL-based feature ingestion" (`v:21.1`).

Weekly run stability decides the choice: batch extraction and transformation fits the stated weekly cadence. “Architecting a Machine Learning Pipeline” is evidence for this value; the brief does not call for continuous ingestion.

### Consequences

* Schedule extraction and transformation ahead of the forecast run.
* Preserve the ingested inputs for historical replay.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because Weekly run stability: fits scheduled batch processing
* Bad, because Past-week reproducibility: requires retained source snapshots

### Streaming feature ingestion

* Good, because Weekly run stability: continuously receives new records
* Bad, because Weekly run stability: adds continuous ingestion operations
