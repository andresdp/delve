# Weekly model training

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for retraining each week, while deployed cameras may be offline.

## Decision Drivers

* Weekly retraining
* Offline devices
* Reproducibility

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Weekly retraining decides the choice: train a candidate model offline on each labelled data batch. This gives up incremental freshness between weekly runs.

### Consequences

* Schedule training against each weekly labelled data snapshot.
* Validate each resulting model before release.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Weekly retraining: fits scheduled offline training
* Good, because Reproducibility: produces discrete model versions
* Bad, because Freshness: waits for next training cycle
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Freshness: updates incrementally
* Bad, because Offline devices: depends on updates reaching devices
* Bad, because Reproducibility: complicates model lineage
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Weekly retraining: supports batch updates
* Bad, because Tight budget: more operational complexity
* Sources: `d:19`, `v:19.3`
