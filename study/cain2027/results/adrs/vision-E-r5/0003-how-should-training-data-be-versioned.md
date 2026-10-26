# How should training data be versioned?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining uses changing labelled images, so the team needs to identify the data used for each model build.

## Decision Drivers

* Changing training data
* Reproducible builds
* Tight budget

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository makes the weekly training inputs identifiable and supports repeatable model builds.

### Consequences

* The team must maintain versioned references to labelled image sets.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data versioning
* Bad, because Additional repository tooling
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versioning with code
* Bad, because May constrain data handling
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Lowest setup effort
* Bad, because Harder to reproduce training inputs
* Sources: `d:11`, `v:11.3`
