# Batch-based learning

*When and how should the model be trained?*

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained every week from newly labelled images.

## Decision Drivers

* Weekly retraining
* New labelled images
* Small team

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

A weekly batch training cycle matches the brief’s retraining cadence and avoids introducing incremental training complexity.

### Consequences

* Training runs on a weekly schedule using newly labelled images.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Fits scheduled retraining
* Good, because Can train offline
* Bad, because Updates arrive in batches
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Can incorporate data incrementally
* Bad, because Not required by weekly cadence
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines batch and incremental updates
* Bad, because More moving parts
* Sources: `d:19`, `v:19.3`
