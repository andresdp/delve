# Retrain on a weekly schedule using batch learning

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies weekly retraining from newly labelled images. Batch learning and a scheduled trigger fit that cadence without requiring incremental training infrastructure.

## Decision Drivers

* weekly retraining
* newly labelled images
* tight budget

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

The brief calls for weekly retraining, so batch learning is a direct fit. Schedule the pipeline weekly to use the newest labelled data available.

### Consequences

* New labels wait for the next scheduled run.
* Provide batch compute for training.

## Pros and Cons of the Options

### Batch-based learning

* Good, because matches weekly cadence
* Good, because offline training
* Bad, because updates arrive on schedule
* Bad, because batch compute needed
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because updates as data arrives
* Good, because may reduce full retraining
* Bad, because more complex update flow
* Bad, because not required by brief
* Sources: `d:19`, `v:19.2`
