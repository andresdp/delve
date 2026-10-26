# Version training data

* System: On-device visual inspection

## Context and Problem Statement

Models are retrained from changing labeled images, so the training input should be identifiable for later review. The design space offers a data version repository and no data versioning (d:11).

## Decision Drivers

* Weekly retraining
* Small team and tight budget

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Weekly retraining decides the choice: identifying each training dataset supports repeatable model builds. The team accepts the added repository overhead despite the tight budget.

### Consequences

* Record the dataset version used for each model build.
* Budget for storage and maintenance of data versions.

## Pros and Cons of the Options

### Data version repository

* Good, because Weekly retraining: identifies training inputs
* Bad, because Small team: adds repository operation
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because Cost: no versioning service to operate
* Bad, because Weekly retraining: weak traceability
* Sources: `d:11`, `v:11.3`
