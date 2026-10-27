# Track training data in a data version repository

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining uses newly labelled images, so each released model should be traceable to its training data.

## Decision Drivers

* Weekly labels
* Reproducibility
* Small team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository makes weekly training inputs identifiable and supports reproducing a model release (d:11, v:11.1).

### Consequences

* Record the data version with each model artifact.
* Manage image storage and retention.

## Pros and Cons of the Options

### Data version repository

* Good, because Explicit data versions
* Good, because Traceable training inputs
* Bad, because Repository upkeep
* Bad, because Storage overhead
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Co-located history
* Good, because Familiar workflow
* Bad, because May burden code repo
* Bad, because Large image data
* Sources: `d:11`, `v:11.2`
