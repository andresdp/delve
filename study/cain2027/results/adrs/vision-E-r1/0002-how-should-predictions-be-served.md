# How should predictions be served?

* System: On-device visual inspection

## Context and Problem Statement

Inspection cameras need predictions even when the line has no network access. The design space includes local and distributed serving options.

## Decision Drivers

* offline operation
* camera-side inference
* tight budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

A local service supports real-time predictions without requiring network access. The checked combination had no warnings, but no attesting sources.

### Consequences

* Run the serving process on or near each camera.
* Manage local service health and resource use.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because local real-time inference
* Good, because no remote service dependency
* Bad, because local runtime to maintain
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because distributed service boundary
* Bad, because network dependency
* Bad, because more infrastructure
* Sources: `d:5`, `v:5.1`
