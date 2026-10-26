# Train centrally and distribute versioned model artifacts

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labelled images, then pushed to production devices. A central training process can produce a consistent artifact for distribution.

## Decision Drivers

* Weekly model updates
* Reproducibility
* Small team

## Considered Options

* Central training with versioned artifacts
* Train separately on each device

## Decision Outcome

Chosen option: "Central training with versioned artifacts".

Reproducibility decides the choice: centrally produced versions give the team a consistent model to release and identify. Devices may lag behind the latest weekly model when offline.

### Consequences

* Training and release infrastructure is needed centrally.
* Each artifact should identify its model version.

## Pros and Cons of the Options

### Central training with versioned artifacts

* Good, because Weekly model updates: one release artifact for devices
* Good, because Reproducibility: versions can be tracked
* Bad, because Network independence: devices may receive updates late

### Train separately on each device

* Good, because Network independence: local training possible
* Bad, because Reproducibility: device results may diverge
* Bad, because Small team: fleet training support
