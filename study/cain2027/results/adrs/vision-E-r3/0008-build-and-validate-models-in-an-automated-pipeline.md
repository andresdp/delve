# Build and validate models in an automated pipeline

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining repeats model building, evaluation, and validation. Automating these steps reduces routine work and creates a consistent release input.

## Decision Drivers

* Weekly retraining
* Small team
* Model pushed to devices

## Considered Options

* Model building pipeline (`v:18.1`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Model building pipeline" (`v:18.1`).

An automated pipeline can train, evaluate, and validate each weekly candidate before packaging it for delivery (d:18, v:18.1).

### Consequences

* Define acceptance criteria before deployment.
* Maintain the training pipeline and its execution environment.

## Pros and Cons of the Options

### Model building pipeline

* Good, because Repeatable validation
* Good, because Automates recurring work
* Bad, because Pipeline maintenance
* Sources: `d:18`, `v:18.1`

### Model building in development tool

* Good, because Simple experimentation
* Bad, because Manual repeatability
* Sources: `d:18`, `v:18.3`
