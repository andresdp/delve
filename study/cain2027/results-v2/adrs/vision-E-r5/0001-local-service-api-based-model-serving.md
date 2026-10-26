# Local service/API based model serving

*How should predictions be served on production devices?*

* System: On-device visual inspection

## Context and Problem Statement

Cameras need local inference because production lines often lack network access.

## Decision Drivers

* Offline operation
* Low latency
* Tight budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Offline operation decides the choice: local serving keeps inference available without network access. This gives up the separation of a distributed service. The design space has no source passages; this choice is grounded in d:5 and v:5.2.

### Consequences

* Inference runs on each device.
* Device resources must support serving.
* Network outages do not block predictions.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Offline operation: serves locally
* Good, because Low latency: avoids network round trips
* Bad, because Tight budget: adds local service management
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Maintainability: separates serving
* Bad, because Offline operation: depends on reachable service
* Bad, because Tight budget: adds service infrastructure
* Sources: `d:5`, `v:5.1`
