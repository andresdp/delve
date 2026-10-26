# Batch-based learning

*When and how should the model be trained?*

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for retraining every week. The design space distinguishes batch, incremental, and hybrid learning.

## Decision Drivers

* weekly retraining
* new labelled images
* small team

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Weekly batch retraining matches the stated cadence and keeps the training workflow bounded. The checked combination had no warnings, but no attesting sources.

### Consequences

* Schedule a weekly training run.
* Validate each candidate before delivery.

## Pros and Cons of the Options

### Batch-based learning

* Good, because fits weekly cadence
* Good, because bounded training runs
* Bad, because updates wait for next run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because learns as data arrives
* Bad, because more frequent model updates
* Sources: `d:19`, `v:19.2`
