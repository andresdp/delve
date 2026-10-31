# Serve predictions through a local device API

* System: On-device visual inspection

## Context and Problem Statement

Cameras need defect predictions where network access is often unavailable. The runtime must work without a remote serving dependency.

## Decision Drivers

* Offline operation
* Device inference

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

A local API supports real-time inference without relying on network access, matching the brief’s device and connectivity constraints (d:5, v:5.2).

### Consequences

* Package and run the model on each device.
* Manage device resource limits.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Local predictions
* Good, because No network dependency
* Bad, because Device resource use
* Bad, because Per-device operations
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Centralized serving
* Good, because Independent deployment
* Bad, because Requires connectivity
* Bad, because Network adds failure modes
* Sources: `d:5`, `v:5.1`
