# How should the application integrate the model?

* System: On-device visual inspection

## Context and Problem Statement

The model runs with the inspection application on devices with limited infrastructure. A separate service would add deployment and network dependencies.

## Decision Drivers

* Offline operation
* Tight infrastructure budget
* Small team

## Considered Options

* Model as module in modular monolith (`v:1.3`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model as module in modular monolith" (`v:1.3`).

Offline operation and budget decide for a model module in the application, giving up independent model-service deployment.

### Consequences

* Application packages must include the model and runtime.
* Model updates follow the device application release path.

## Pros and Cons of the Options

### Model as module in modular monolith

* Good, because Offline: embeds inference with application
* Good, because Budget: avoids separate service
* Bad, because Small team: application and model releases are coupled
* Sources: `d:1`, `v:1.3`

### Model as a service

* Good, because Small team: model has a service boundary
* Bad, because Offline: service availability must be maintained
* Sources: `d:1`, `v:1.1`
