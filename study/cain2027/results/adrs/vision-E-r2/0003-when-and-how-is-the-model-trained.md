# When and how is the model trained?

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies retraining each week from newly labelled images. The design space offers batch, incremental, and hybrid learning (d:19).

## Decision Drivers

* Weekly retraining
* New labelled images
* Offline devices

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Weekly labelled data naturally fits offline batch training, which can produce a model package for later device delivery (d:19, v:19.1).

### Consequences

* Training runs on a schedule against accumulated labels.
* Device inference can continue on its current model during training.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Fits scheduled retraining
* Good, because Produces discrete model versions
* Bad, because Training waits for batch
* Bad, because Requires training resources
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Uses data as it arrives
* Good, because Can update continuously
* Bad, because More complex update path
* Bad, because Less aligned with weekly cadence
* Sources: `d:19`, `v:19.2`
