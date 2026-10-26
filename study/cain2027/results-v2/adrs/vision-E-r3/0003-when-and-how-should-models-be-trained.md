# When and how should models be trained?

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive weekly, and the brief does not require learning from each image as it arrives. Training can happen centrally, apart from offline inference.

## Decision Drivers

* Weekly retraining
* Tight infrastructure budget

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Tight budget decides for batch training on the weekly cadence; this gives up immediate use of newly labelled images.

### Consequences

* Training requires a weekly data and compute window.
* Validated model artifacts need a delivery path to devices.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Budget: trains in scheduled batches
* Bad, because Weekly retraining: changes wait for the next run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Weekly retraining: can incorporate new data continuously
* Bad, because Budget: requires an ongoing training path
* Sources: `d:19`, `v:19.2`
