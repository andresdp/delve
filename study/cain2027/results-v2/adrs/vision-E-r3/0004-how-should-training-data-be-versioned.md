# How should training data be versioned?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining depends on labelled images, and reproducibility requires identifying which data produced each model. Dedicated version support costs additional setup and upkeep.

## Decision Drivers

* Reproducibility
* Small team
* Tight infrastructure budget

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducibility decides for explicit data versioning, accepting its maintenance cost so a model can be linked to its training data.

### Consequences

* Dataset versions and model artifacts need linked identifiers.
* The team must maintain versioned data storage.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: tracks dataset versions
* Bad, because Small team: adds a repository to maintain
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because Budget: avoids versioning infrastructure
* Bad, because Reproducibility: training inputs are harder to recover
* Sources: `d:11`, `v:11.3`
