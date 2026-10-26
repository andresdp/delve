# Retain labelled images and training inputs as a reproducible dataset snapshot

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images drive weekly retraining. Preserving the inputs used for each release supports reproduction and investigation of model changes.

## Decision Drivers

* Reproducibility
* Weekly model updates
* Infrastructure cost

## Considered Options

* Snapshot training inputs per release
* Train from a mutable latest dataset

## Decision Outcome

Chosen option: "Snapshot training inputs per release".

Reproducibility decides the choice because weekly model behavior should be traceable to its labelled inputs. This uses additional storage and retention effort.

### Consequences

* Each model release needs a reference to its dataset snapshot.
* Storage requirements grow with retained snapshots.

## Pros and Cons of the Options

### Snapshot training inputs per release

* Good, because Reproducibility: preserves training data identity
* Good, because Weekly model updates: supports release comparison
* Bad, because Infrastructure cost: stores repeated data or snapshots

### Train from a mutable latest dataset

* Good, because Infrastructure cost: avoids snapshot retention
* Bad, because Reproducibility: inputs can change after training
* Bad, because Weekly model updates: comparisons become ambiguous
