# How should training data be versioned?

* System: On-device visual inspection

## Context and Problem Statement

Weekly training must be repeatable against specific newly labelled image sets.

## Decision Drivers

* Reproducibility
* Weekly updates
* Tight budget

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducibility decides the choice: versioned data makes weekly training inputs identifiable. This gives up some simplicity and storage budget. The design space has no source passages; this choice is grounded in d:11 and v:11.1.

### Consequences

* Each model release links to a dataset version.
* Versioned images consume storage.
* Training runs can be traced to inputs.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: identifies training data versions
* Good, because Weekly updates: tracks successive image sets
* Bad, because Tight budget: adds repository tooling and storage
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because Tight budget: avoids versioning infrastructure
* Bad, because Reproducibility: cannot reliably identify training set
* Sources: `d:11`, `v:11.3`
