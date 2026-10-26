# Local service/API based model serving

*How should predictions be served?*

* System: On-device visual inspection

## Context and Problem Statement

Inspection must continue when a camera has no network access. Predictions need to reach the local production application in real time.

## Decision Drivers

* Network independence
* Low latency
* Tight budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Network independence decides the choice, with low latency also favoring local inference. The trade-off is operating a local serving interface on each device.

### Consequences

* The camera application calls a device-local endpoint.
* Local service health and resource use need operational attention.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Network independence: serves predictions locally
* Good, because Low latency: avoids remote inference round trips
* Bad, because Tight budget: adds local service/API operations
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Separation: model serving is distributed
* Bad, because Network independence: remote calls can fail offline
* Bad, because Low latency: network adds delay
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because Tight budget: scheduled batch processing
* Bad, because Low latency: results are not immediate
* Sources: `d:5`, `v:5.3`
