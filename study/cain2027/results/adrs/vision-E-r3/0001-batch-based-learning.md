# Batch-based learning

*How to train the model?*

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labelled images. Training can run centrally in batches, independently of device connectivity.

## Decision Drivers

* Weekly retraining
* New labelled images
* Small team

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Weekly retraining fits batch learning, which can run offline; incremental training is not required by the brief. The design point has no warnings, but no attesting sources.

### Consequences

* Schedule a weekly training run.
* Collect and label images before each run.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Fits weekly retraining
* Good, because Can run offline
* Bad, because Updates wait for batch
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Can incorporate data continuously
* Bad, because Adds operational complexity
* Sources: `d:19`, `v:19.2`
