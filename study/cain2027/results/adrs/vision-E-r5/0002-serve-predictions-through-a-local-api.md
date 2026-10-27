# Serve predictions through a local API

* System: On-device visual inspection

## Context and Problem Statement

The inspection application needs timely predictions while cameras may be disconnected. A local service provides real-time predictions without relying on a remote endpoint.

## Decision Drivers

* offline operation
* real-time inspection

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Local serving matches on-device inspection and avoids requiring network access for predictions.

### Consequences

* Run and monitor a prediction endpoint on each device.
* Keep the model available locally.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because local real-time predictions
* Good, because works offline
* Bad, because local service to operate
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because service boundary
* Good, because centralized serving
* Bad, because network dependent
* Bad, because distributed operations
* Sources: `d:5`, `v:5.1`
