# Run inspection inference on the production-line devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras must inspect items where network access is often unavailable. The architecture needs to place prediction close to image capture.

## Decision Drivers

* Intermittent network
* On-line inspection

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

This matches inspection on cameras during network outages. Sources *Composing Deep-Learning Microservices for the Hybrid Internet of Things*, *Three Levels of ML Software*, and Microsoft’s *MLOps: Model management, deployment, and monitoring with Azure Machine Learning* describe this placement (s07_p01, s19_p11, s25_p07).

### Consequences

* Package and deploy the model to each device.
* Plan for device-specific resource limits and updates.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Runs at the device
* Good, because Works without network
* Bad, because Device resources constrain models
* Bad, because Device rollout required
* Sources: `s07_p01`, `s19_p11`, `s25_p07`

### Model-as-a-service deployment

* Good, because Centralized serving
* Good, because Shared runtime
* Bad, because Depends on connectivity
* Bad, because Adds network latency
* Sources: `s01_p08`, `s06_p13`, `s19_p08`
