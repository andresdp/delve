# Embed the model as a module in the camera application

* System: On-device visual inspection

## Context and Problem Statement

Cameras need to inspect images without network access. A model module keeps inference in the application on each device.

## Decision Drivers

* offline inference
* small team

## Considered Options

* Model as module in modular monolith (`v:1.3`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model as module in modular monolith" (`v:1.3`).

A local module supports inference when cameras have no network access and keeps the deployment model manageable for a small team.

### Consequences

* Package the model with the camera application.
* Update application and model together.

## Pros and Cons of the Options

### Model as module in modular monolith

* Good, because local inference
* Good, because clear module boundary
* Bad, because app and model deploy together
* Sources: `d:1`, `v:1.3`

### Model as a service

* Good, because separate model service
* Good, because independent interface
* Bad, because distributed service overhead
* Bad, because network dependency
* Sources: `d:1`, `v:1.1`
