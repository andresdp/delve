# Distribute weekly models for local installation

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly and pushed to devices that may lack network access. Updates must fit intermittent connectivity.

## Decision Drivers

* Offline operation
* Weekly model freshness
* Low infrastructure cost

## Considered Options

* Device-initiated downloads
* Staged, resumable model packages
* Manual removable-media updates

## Decision Outcome

Chosen option: "Staged, resumable model packages".

Offline operation decides the choice: staged packages can be fetched when connected and installed later. This gives up the simplicity of direct downloads and requires rollout tracking.

### Consequences

* Define package versioning and integrity checks.
* Devices need storage for staged packages and the active model.

## Pros and Cons of the Options

### Device-initiated downloads

* Good, because Infrastructure cost: uses straightforward distribution
* Bad, because Offline operation: devices cannot fetch while disconnected
* Bad, because Model freshness: update timing depends on connectivity

### Staged, resumable model packages

* Good, because Offline operation: packages can wait for connectivity
* Good, because Model freshness: supports controlled weekly rollout
* Bad, because Infrastructure cost: requires package hosting and rollout tracking

### Manual removable-media updates

* Good, because Offline operation: works without network access
* Bad, because Low infrastructure cost: adds operator effort
* Bad, because Model freshness: rollout can be slow
