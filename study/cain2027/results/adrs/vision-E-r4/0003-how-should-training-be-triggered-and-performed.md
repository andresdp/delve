# How should training be triggered and performed?

* System: On-device visual inspection

## Context and Problem Statement

Newly labeled images arrive for weekly retraining. The brief specifies a recurring cadence rather than continuous updates.

## Decision Drivers

* Weekly retraining
* New labeled images

## Considered Options

* On-schedule trigger with batch-based learning (`v:12.3`)
* On availability of new training data trigger with incremental learning (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger with batch-based learning" (`v:12.3`).

Weekly batch retraining directly follows the stated cadence and supports a controlled training run (d:12, v:12.3; d:19, v:19.1).

### Consequences

* Training runs weekly against accumulated labels.
* Fresh labels wait until the next scheduled run.

## Pros and Cons of the Options

### On-schedule trigger with batch-based learning

* Good, because Matches weekly cadence
* Good, because Repeatable training runs
* Bad, because Waits for scheduled run
* Sources: `d:12`, `v:12.3`, `d:19`, `v:19.1`

### On availability of new training data trigger with incremental learning

* Good, because Uses new data quickly
* Bad, because More frequent updates
* Bad, because Incremental process complexity
* Sources: `d:12`, `v:12.4`, `d:19`, `v:19.2`
