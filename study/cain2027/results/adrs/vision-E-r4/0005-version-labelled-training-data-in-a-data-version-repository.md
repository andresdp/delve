# Version labelled training data in a data version repository

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining uses newly labelled images. Keeping track of dataset versions makes training inputs identifiable across releases.

## Decision Drivers

* Weekly retraining
* Labelled images
* Release traceability

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository supports identifying the labelled-image set used for each weekly training run (d:11, v:11.1).

### Consequences

* The team must retain dataset version references with model releases.
* Repository operation adds a small infrastructure cost.

## Pros and Cons of the Options

### Data version repository

* Good, because Purpose-built data versioning
* Good, because Identifies training inputs
* Bad, because Repository adds a tool to manage
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versioning with code
* Bad, because May add repository overhead
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because No versioning setup
* Bad, because Training inputs harder to identify
* Sources: `d:11`, `v:11.3`
