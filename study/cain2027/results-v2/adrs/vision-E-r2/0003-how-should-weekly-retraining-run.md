# How should weekly retraining run?

* System: On-device visual inspection

## Context and Problem Statement

The team retrains from newly labelled images every week. The workspace describes scheduled triggers and batch-based learning as alternatives for pipeline execution and training.

## Decision Drivers

* Weekly retraining
* Tight budget
* Reproducibility

## Considered Options

* On-schedule trigger with batch-based learning (`v:12.3`)
* On availability of new training data trigger with batch-based learning (`v:12.4`)
* On-demand trigger with incremental learning (`v:12.1`)

## Decision Outcome

Chosen option: "On-schedule trigger with batch-based learning" (`v:12.3`).

The stated weekly cadence decides the choice: scheduled batch training keeps execution predictable and bounded. It gives up immediate use of labels added between runs.

### Consequences

* Schedule the retraining pipeline weekly.
* A failed run delays the next model unless operators rerun it.

## Pros and Cons of the Options

### On-schedule trigger with batch-based learning

* Good, because Weekly retraining: scheduled runs match the cadence
* Good, because Tight budget: trains only on the weekly schedule
* Bad, because Freshness: labels arriving just after a run wait until the next run
* Sources: `d:12`, `v:12.3`, `d:19`, `v:19.1`

### On availability of new training data trigger with batch-based learning

* Good, because Freshness: starts when new data is available
* Bad, because Tight budget: irregular runs may use more resources
* Sources: `d:12`, `v:12.4`, `d:19`, `v:19.1`

### On-demand trigger with incremental learning

* Good, because Control: operators decide when to run
* Bad, because Weekly retraining: depends on manual or external triggering
* Sources: `d:12`, `v:12.1`, `d:19`, `v:19.2`
