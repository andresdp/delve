# Train models in weekly batches

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies a weekly retraining cycle from newly labelled images, which naturally supports an offline training run.

## Decision Drivers

* Weekly cadence
* New labels
* Offline production

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch training directly matches the stated weekly retraining schedule and can run separately from disconnected production devices (d:19, v:19.1).

### Consequences

* Schedule and validate the weekly training job.
* New labels affect production after the next release.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Matches weekly cycle
* Good, because Runs offline
* Bad, because Updates await next run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Frequent updates
* Good, because Uses new data promptly
* Bad, because More operational complexity
* Bad, because May need continuous availability
* Sources: `d:19`, `v:19.2`
