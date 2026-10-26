# How are predictions served?

* System: On-device visual inspection

## Context and Problem Statement

Cameras need defect predictions while disconnected. The design space distinguishes local API serving from distributed and batch approaches (d:5).

## Decision Drivers

* Offline inference
* On-line inspection
* Low infrastructure cost

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Local serving provides real-time predictions at the camera without relying on network connectivity (d:5, v:5.2).

### Consequences

* The camera must host and operate the serving interface.
* Serving capacity is limited by device resources.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Local real-time predictions
* Good, because No remote service required
* Bad, because Local service to operate
* Bad, because Device resource use
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Centralized serving
* Good, because Service isolation
* Bad, because Network dependency
* Bad, because Additional infrastructure
* Sources: `d:5`, `v:5.1`
