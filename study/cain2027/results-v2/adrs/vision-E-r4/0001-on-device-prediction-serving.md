# On-device prediction serving

* System: On-device visual inspection

## Context and Problem Statement

Cameras need defect predictions on production lines where network access is often unavailable.

## Decision Drivers

* Offline availability
* Low latency
* Tight budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Offline availability decides the choice: local serving can keep inspecting when disconnected. It costs device resources compared with centralized serving.

### Consequences

* Package and update a local prediction service.
* Plan for device compute and storage limits.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Offline availability: serves locally
* Good, because Low latency: avoids network round trip
* Bad, because Tight budget: devices need serving resources
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Central operation: shared service
* Bad, because Offline availability: requires network
* Bad, because Low latency: network round trip
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because Tight budget: scheduled processing
* Bad, because Low latency: predictions are delayed
* Sources: `d:5`, `v:5.3`
