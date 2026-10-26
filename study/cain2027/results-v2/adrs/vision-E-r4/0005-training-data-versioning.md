# Training data versioning

* System: On-device visual inspection

## Context and Problem Statement

Weekly model retraining uses newly labelled images; linking each model to its training data helps reproduce and investigate releases.

## Decision Drivers

* Reproducibility
* Weekly retraining
* Tight budget

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducibility decides the choice: record the image dataset version used for each weekly model. This adds storage and tooling costs for the small team.

### Consequences

* Keep dataset references with each model artifact.
* Budget for storage of versioned image data.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: records dataset versions
* Bad, because Tight budget: adds repository tooling and storage
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Tight budget: uses existing repository workflow
* Bad, because Weekly retraining: large image datasets strain code repositories
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Tight budget: avoids added tooling
* Bad, because Reproducibility: cannot reliably recover training inputs
* Sources: `d:11`, `v:11.3`
