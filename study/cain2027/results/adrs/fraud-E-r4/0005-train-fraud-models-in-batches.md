# Train fraud models in batches

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires serving scores quickly and identifying which model version produced each score; it does not require the model to learn during scoring. The workspace offers batch and incremental learning. (d:19)

## Decision Drivers

* Traceable model versions
* Separate training from serving

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch training supports identifiable model releases while keeping training out of the transaction scoring path. This choice is an architectural inference from auditability; the workspace point check returned no warnings, though it was unattested. (d:19, v:19.1)

### Consequences

* Model updates arrive on a training schedule.
* Training data and artifacts need version records.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Discrete model versions
* Good, because Training can run offline
* Bad, because Updates are periodic
* Bad, because Training needs batch data
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Can incorporate data incrementally
* Good, because Potentially fresher model
* Bad, because Model changes over time
* Bad, because Harder version attribution
* Sources: `d:19`, `v:19.2`
