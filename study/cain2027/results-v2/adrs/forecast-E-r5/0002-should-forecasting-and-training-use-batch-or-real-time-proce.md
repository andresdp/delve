# Should forecasting and training use batch or real-time processing?

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly demand forecasts. The brief gives no real-time prediction requirement.

## Decision Drivers

* Weekly run
* Reproducibility
* Fast iteration

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

The weekly run decides the choice: batch processing fits the stated cadence and makes each run’s inputs easier to reproduce. This gives up immediate processing of new data.

### Consequences

* Run forecasts against a defined weekly data snapshot.
* No real-time processing path is established.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Weekly run: aligns to weekly cadence
* Good, because Reproducibility: bounded input snapshot
* Bad, because Fast iteration: changes wait for next run
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Fast iteration: responds to incoming data
* Bad, because Weekly run: extra continuous-processing complexity
* Bad, because Reproducibility: changing inputs are harder to replay
* Sources: `d:15`, `v:15.2`
