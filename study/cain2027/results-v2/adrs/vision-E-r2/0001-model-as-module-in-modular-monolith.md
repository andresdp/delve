# Model as module in modular monolith

*How should inference run on production cameras?*

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect defects on production lines, often without network access. Inference must remain available locally.

## Decision Drivers

* Network independence
* Low latency
* Tight budget

## Considered Options

* Model as module in modular monolith (`v:1.3`)
* Model as a service (`v:1.1`)
* Model in monolith (`v:1.2`)

## Decision Outcome

Chosen option: "Model as module in modular monolith" (`v:1.3`).

Network independence decides the choice: package inference with the camera application while keeping a module boundary. This gives up independent model service deployment.

### Consequences

* Bundle model runtime and application for each device.
* Model updates require a coordinated device release.

## Pros and Cons of the Options

### Model as module in modular monolith

* Good, because Network independence: runs with the application
* Good, because Tight budget: avoids separate service infrastructure
* Bad, because Weekly updates: coordinate model and application releases
* Sources: `d:1`, `v:1.3`

### Model as a service

* Good, because Separation: model can be managed independently
* Bad, because Network independence: service may require connectivity
* Bad, because Tight budget: adds service operations
* Sources: `d:1`, `v:1.1`

### Model in monolith

* Good, because Network independence: embed model in application
* Bad, because Weekly updates: model changes are coupled to application code
* Sources: `d:1`, `v:1.2`
