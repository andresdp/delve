# Run inference through a local device service

* System: On-device visual inspection

## Context and Problem Statement

Production cameras often lack network access, so prediction serving must remain available on the device.

## Decision Drivers

* Intermittent network
* Camera line inference
* Low infrastructure budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Local serving keeps defect inference available when the production line has no network connection (d:5, v:5.2).

### Consequences

* Package the model with its local serving runtime.
* Provision and monitor device compute and storage.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Works without network
* Good, because Keeps inference local
* Bad, because Device resource limits
* Bad, because Local operations required
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Centralized operation
* Good, because Shared serving capacity
* Bad, because Needs network access
* Bad, because Adds infrastructure
* Sources: `d:5`, `v:5.1`
