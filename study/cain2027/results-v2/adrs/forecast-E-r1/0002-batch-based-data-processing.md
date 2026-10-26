# Batch-based data processing

*Process weekly data in batches or streams?*

* System: Retail demand forecasting

## Context and Problem Statement

The system processes weekly demand, and the brief specifies a weekly production run without a real-time requirement (d:15).

## Decision Drivers

* Weekly run
* Reproducibility
* Small team

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

The weekly run decides the choice: batch processing fits the stated cadence and keeps the pipeline manageable, at the cost of not processing demand data continuously.

### Consequences

* Schedule data preparation around the weekly forecast run.
* Capture the batch inputs and cutoff used for each run.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Weekly run: aligns processing to the forecast cadence
* Good, because Small team: simpler scheduled workflow
* Bad, because Weekly run: results wait for the batch window
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Weekly run: can process arriving data continuously
* Bad, because Small team: adds streaming operations
* Bad, because Reproducibility: requires tracking event-time inputs
* Sources: `d:15`, `v:15.2`
