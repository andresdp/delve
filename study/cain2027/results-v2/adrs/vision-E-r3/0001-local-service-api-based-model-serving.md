# Local service/API based model serving

*How should predictions run on production cameras?*

* System: On-device visual inspection

## Context and Problem Statement

Inspection must continue when network access is unavailable. Predictions are needed at the line, so serving should be local.

## Decision Drivers

* Offline operation
* Low prediction latency

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Offline operation decides the choice: local serving keeps inspection available without network access, at the cost of maintaining a local service.

### Consequences

* Each device needs a compatible model runtime.
* Model updates must reach devices locally.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Offline: serves predictions locally
* Good, because Latency: avoids remote round trips
* Bad, because Cost: requires local service upkeep
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Latency: real-time service interface
* Bad, because Offline: depends on service reachability
* Sources: `d:5`, `v:5.1`
