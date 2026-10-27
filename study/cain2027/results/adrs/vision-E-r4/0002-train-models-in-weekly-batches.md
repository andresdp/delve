# Train models in weekly batches

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for retraining each week. This calls for a repeatable training cycle.

## Decision Drivers

* Weekly retraining
* Small team
* Tight budget

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

A weekly labelled-image cycle aligns with batch training, which can run offline (d:19, v:19.1).

### Consequences

* Training runs on a weekly schedule.
* The model reflects labels available at each run.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Fits scheduled retraining
* Good, because Offline training possible
* Bad, because Updates arrive on batch cadence
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Updates incrementally
* Good, because Can learn online
* Bad, because More frequent update handling
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines training modes
* Bad, because More moving parts
* Sources: `d:19`, `v:19.3`
