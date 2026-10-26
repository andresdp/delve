# How should the application serve predictions?

* System: On-device visual inspection

## Context and Problem Statement

Inspection must continue when production cameras cannot reach a network service. The serving path should run locally on each device.

## Decision Drivers

* Offline operation
* Real-time inspection

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

A local serving interface gives the camera application real-time predictions without requiring network access (d:5, v:5.2).

### Consequences

* The service and model must be deployed on each device.
* Local API compatibility needs management.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Local predictions
* Good, because Clear API boundary
* Bad, because Local service upkeep
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Separate deployment
* Bad, because Network dependency
* Bad, because More infrastructure
* Sources: `d:5`, `v:5.1`
