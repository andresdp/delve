# Model in monolith

*How is the model integrated?*

* System: On-device visual inspection

## Context and Problem Statement

The defect model must run on cameras that often have no network access. The design space includes embedded and service based integration options (d:1).

## Decision Drivers

* Offline operation
* Small team
* Tight budget

## Considered Options

* Model in monolith (`v:1.2`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model in monolith" (`v:1.2`).

Embedding the model in the camera application supports inference without network access and keeps the deployment shape simple for a small team (d:1, v:1.2).

### Consequences

* Model updates require application package delivery.
* Each device needs sufficient compute and storage.

## Pros and Cons of the Options

### Model in monolith

* Good, because Runs with application
* Good, because No network dependency
* Bad, because Ties model to application release
* Bad, because Device resource limits
* Sources: `d:1`, `v:1.2`

### Model as a service

* Good, because Separate model lifecycle
* Good, because Clear interface
* Bad, because Service operations overhead
* Bad, because May depend on network
* Sources: `d:1`, `v:1.1`
