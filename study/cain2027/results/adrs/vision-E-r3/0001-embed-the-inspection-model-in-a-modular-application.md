# Embed the inspection model in a modular application

* System: On-device visual inspection

## Context and Problem Statement

Each camera must inspect images without network access. The brief does not require independently scaling inference services.

## Decision Drivers

* Offline inference
* Tight infrastructure budget

## Considered Options

* Model as module in modular monolith (`v:1.3`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model as module in modular monolith" (`v:1.3`).

A local model module supports disconnected inference and keeps the runtime footprint small (d:1, v:1.3).

### Consequences

* Package the model with the camera application.
* Update the application when deploying a model.

## Pros and Cons of the Options

### Model as module in modular monolith

* Good, because Local inference
* Good, because Simple deployment
* Bad, because Coupled release
* Sources: `d:1`, `v:1.3`

### Model as a service

* Good, because Independent model service
* Bad, because Service operations
* Bad, because Network dependency
* Sources: `d:1`, `v:1.1`
