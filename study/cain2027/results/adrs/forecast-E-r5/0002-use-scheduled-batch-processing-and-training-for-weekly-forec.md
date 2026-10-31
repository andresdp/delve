# Use scheduled batch processing and training for weekly forecasts

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly store and product forecasts, making a scheduled batch workflow a direct fit. The design space distinguishes batch from stream processing and batch from incremental learning (d:15, d:19).

## Decision Drivers

* Weekly forecast cadence
* Small team ownership

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)
* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Weekly forecasts do not require real-time processing in the brief, so scheduled batches keep the workflow aligned with the delivery cadence. Choose batch-based learning as well for repeatable retraining; these are separate design dimensions (d:15, d:19).

### Consequences

* Run forecast generation on a weekly schedule.
* Reruns need the original data and model inputs.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Fits scheduled weekly work
* Good, because Straightforward historical reruns
* Bad, because Results arrive on a schedule
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes incoming data promptly
* Bad, because Adds streaming complexity
* Sources: `d:15`, `v:15.2`

### Batch-based learning

* Good, because Repeatable offline training
* Good, because Fits periodic refresh
* Bad, because Model updates await next training run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Can update as data arrives
* Bad, because Adds online training complexity
* Sources: `d:19`, `v:19.2`
