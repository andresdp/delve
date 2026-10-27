# Local service/API based model serving

*How to serve predictions on devices?*

* System: On-device visual inspection

## Context and Problem Statement

Cameras run inspection along production lines, often without network access. Prediction delivery therefore needs to work locally on the device.

## Decision Drivers

* Offline operation
* Camera inspection
* Tight budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Local serving keeps inference on the device when the network is unavailable. The design point has no warnings, but no attesting sources.

### Consequences

* Package the model and runtime for each device.
* Plan for local model updates.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Serves predictions locally
* Good, because Works without remote service
* Bad, because Requires device packaging
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Distributed service boundary
* Bad, because Depends on network access
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because Processes scheduled batches
* Bad, because Does not fit immediate inspection
* Sources: `d:5`, `v:5.3`
