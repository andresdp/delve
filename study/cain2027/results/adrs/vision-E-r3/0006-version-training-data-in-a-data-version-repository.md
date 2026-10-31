# Version training data in a data version repository

* System: On-device visual inspection

## Context and Problem Statement

The team retrains from newly labelled images each week. Linking each model release to the data used for training supports repeatable builds and investigation.

## Decision Drivers

* Weekly training
* Traceable model releases

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Versioning the weekly training inputs helps relate a deployed model to its labelled data, despite the added repository maintenance (d:11, v:11.1).

### Consequences

* Record the data version alongside each model artifact.
* Manage storage for retained image versions.

## Pros and Cons of the Options

### Data version repository

* Good, because Explicit data versions
* Good, because Reproducible training inputs
* Bad, because Repository upkeep
* Bad, because Storage overhead
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because Less setup
* Bad, because Harder to reproduce runs
* Sources: `d:11`, `v:11.3`
