# How should training data be versioned?

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images feed recurring model training. Reproducing a model requires identifying which data version produced it.

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

Reproducibility decides the choice because weekly retraining must be traceable to its labelled images. It costs the small team additional repository operations.

### Consequences

* Record the data version alongside each trained model.
* Maintain the repository as part of the training workflow.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: records specific data versions
* Bad, because Tight budget: adds repository setup and maintenance
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Tight budget: keeps versioning near existing code
* Bad, because Reproducibility: large image datasets may be awkward to manage
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Tight budget: no added versioning system
* Bad, because Reproducibility: training inputs cannot be reliably restored
* Sources: `d:11`, `v:11.3`
