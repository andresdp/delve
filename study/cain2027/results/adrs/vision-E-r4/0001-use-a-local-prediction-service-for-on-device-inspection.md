# Use a local prediction service for on-device inspection

* System: On-device visual inspection

## Context and Problem Statement

Cameras need defect predictions where network access is often unavailable. Serving must work at the production line.

## Decision Drivers

* Offline operation
* Camera integration

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Local serving supports real-time inspection without relying on network connectivity; the design space lists it as an accepted option (d:5, v:5.2).

### Consequences

* Each device must carry and run the model.
* Device resources constrain inference capacity.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Runs locally
* Good, because Real-time predictions
* Bad, because Device deployment needed
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Distributed service
* Good, because Centralized serving
* Bad, because Depends on network
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because Scheduled processing
* Good, because Writes results to storage
* Bad, because Not immediate
* Sources: `d:5`, `v:5.3`
