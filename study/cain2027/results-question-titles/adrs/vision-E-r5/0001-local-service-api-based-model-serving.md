# Local service/API based model serving

*How should the model serve predictions?*

* System: On-device visual inspection

## Context and Problem Statement

Cameras need local defect predictions on production lines that often lack network access.

## Decision Drivers

* Intermittent connectivity
* On-device inference
* Tight budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

A local service can make predictions on-device without requiring a network connection, matching the deployment setting.

### Consequences

* Each device must run and expose the local prediction service.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Runs locally
* Good, because Real-time predictions
* Bad, because Requires local service operation
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Distributed service boundary
* Bad, because Depends on network access
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because Scheduled processing
* Bad, because Predictions are not immediate
* Sources: `d:5`, `v:5.3`
