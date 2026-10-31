# Schedule retraining weekly as a batch job

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies weekly retraining from newly labelled images. It does not require training to happen continuously as images arrive.

## Decision Drivers

* Weekly cadence
* New labelled images
* Tight budget

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

A batch job follows the stated weekly retraining cadence and can run independently of the devices’ network availability (d:19, v:19.1).

### Consequences

* Collect labelled images for each training run.
* Coordinate training completion with device rollout.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Matches weekly cadence
* Good, because Can train offline
* Bad, because Updates wait for next run
* Bad, because Requires a batch data set
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Can incorporate data continuously
* Good, because Avoids full batch retraining
* Bad, because Adds online training complexity
* Bad, because Not required by the brief
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines training modes
* Good, because Flexible update timing
* Bad, because More operational complexity
* Bad, because Unneeded for stated cadence
* Sources: `d:19`, `v:19.3`
