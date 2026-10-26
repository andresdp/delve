# Where should inference run?

* System: On-device visual inspection

## Context and Problem Statement

Production cameras must keep detecting defects when network access is unavailable. The brief explicitly requires inference on the devices.

## Decision Drivers

* Offline operation
* Reliable inspection
* Low infrastructure cost

## Considered Options

* On-device edge inference (`v:30.4`)
* Containerized inference deployment (`v:30.19`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Offline operation decides the choice: local inference remains available without network access. This gives up centralized deployment simplicity and makes device update delivery a requirement.

### Consequences

* Inference executes locally on each camera device.
* Model distribution must reach devices when connectivity is available.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Offline operation: inference runs on device
* Good, because Low infrastructure cost: avoids serving infrastructure
* Bad, because Weekly updates: devices need a delivery path
* Bad, because Reproducibility: device environments need control
* Sources: `s01_p06`, `s07_p01`, `s19_p11`, `s24_p01`, `s25_p07`

### Containerized inference deployment

* Good, because Reproducibility: bundles inference dependencies
* Good, because Deployment flexibility: supports multiple runtimes
* Bad, because Offline operation: remote serving depends on connectivity
* Bad, because Low infrastructure cost: requires container runtime infrastructure
* Sources: `s04_p02`, `s06_p07`, `s07_p03`, `s19_p17`
