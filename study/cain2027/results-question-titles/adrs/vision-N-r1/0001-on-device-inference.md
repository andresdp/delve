# On-device inference

*Where should defect inference run?*

* System: On-device visual inspection

## Context and Problem Statement

Production cameras inspect items even when the line has no network access. Detection therefore needs to work at the device or depend on a local network service.

## Decision Drivers

* Offline operation
* Production-line cameras

## Considered Options

* On-device inference
* Central inference service

## Decision Outcome

Chosen option: "On-device inference".

It can keep inspecting products when network access is unavailable, which is a stated operating condition. It places model execution and resource constraints on the cameras or their attached devices.

### Consequences

* Devices need compatible inference hardware and runtime.
* Model updates must reach and install on devices.

## Pros and Cons of the Options

### On-device inference

* Good, because Works without network
* Good, because Low network traffic
* Bad, because Device compute limits
* Bad, because Fleet deployment burden

### Central inference service

* Good, because Centralized compute
* Good, because Simpler model hosting
* Bad, because Requires connectivity
* Bad, because Network adds latency
