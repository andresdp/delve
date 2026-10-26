# Package each model as a versioned release

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly and pushed to production devices. Releases need a clear identity so teams can tell which model a device is running and reproduce a deployment.

## Decision Drivers

* Reproducibility
* Weekly model updates
* Small team

## Considered Options

* Versioned model artifact with training metadata
* Replace the model file in place

## Decision Outcome

Chosen option: "Versioned model artifact with training metadata".

Reproducibility decides the choice: the team needs to identify and recreate weekly releases. This costs extra packaging effort for each update.

### Consequences

* Each release must retain its model and associated training metadata.
* Devices and deployment records need to identify the release version.

## Pros and Cons of the Options

### Versioned model artifact with training metadata

* Good, because Reproducibility: ties model to training inputs and settings
* Good, because Small team: clear release identity
* Bad, because Weekly model updates: requires release packaging work

### Replace the model file in place

* Good, because Weekly model updates: minimal packaging
* Bad, because Reproducibility: loses prior release identity
* Bad, because Small team: harder to diagnose device differences
