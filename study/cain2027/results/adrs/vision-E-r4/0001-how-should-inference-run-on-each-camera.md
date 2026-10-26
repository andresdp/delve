# How should inference run on each camera?

* System: On-device visual inspection

## Context and Problem Statement

Cameras need predictions while often offline. The model must stay close to the production line.

## Decision Drivers

* Offline inference
* Small team
* Tight budget

## Considered Options

* Model as module in modular monolith (`v:1.3`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model as module in modular monolith" (`v:1.3`).

Embedding the model with the camera application supports offline inference and keeps the runtime footprint small (d:1, v:1.3).

### Consequences

* Application and model ship together.
* Each device needs a local model artifact.

## Pros and Cons of the Options

### Model as module in modular monolith

* Good, because Embedded execution
* Good, because Simple deployment
* Bad, because Tied to application release
* Sources: `d:1`, `v:1.3`

### Model as a service

* Good, because Independent model boundary
* Bad, because Service operations
* Bad, because Network dependency
* Sources: `d:1`, `v:1.1`
