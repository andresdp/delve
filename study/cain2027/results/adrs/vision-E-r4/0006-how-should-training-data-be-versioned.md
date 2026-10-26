# How should training data be versioned?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining uses newly labeled images, and model releases need to be traceable to the data used to train them.

## Decision Drivers

* Changing labeled data
* Reproducible training
* Small team

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A versioned data repository links each retraining run to its input image set and supports reproducibility (d:11, v:11.1).

### Consequences

* The team must maintain data references and metadata.
* Training runs can be tied to specific data versions.

## Pros and Cons of the Options

### Data version repository

* Good, because Explicit data history
* Good, because Reproducible inputs
* Bad, because Repository upkeep
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because Less setup
* Bad, because Harder to reproduce runs
* Sources: `d:11`, `v:11.3`
