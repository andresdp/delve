# Train models in batches

* System: On-device visual inspection

## Context and Problem Statement

Newly labeled images arrive for weekly retraining; the brief does not call for learning during production inference. The design space distinguishes batch and incremental learning (d:19).

## Decision Drivers

* Weekly retraining
* Small team and tight budget

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Weekly retraining decides the choice: batch learning fits the stated cadence and avoids continuous-training complexity. New labels wait for the next run.

### Consequences

* Schedule a training run each week.
* Validate each trained model before release.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Weekly retraining: fits scheduled runs
* Good, because Cost: bounded training runs
* Bad, because Weekly retraining: waits for next run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Weekly retraining: can incorporate data continuously
* Bad, because Small team: more training-state complexity
* Sources: `d:19`, `v:19.2`
