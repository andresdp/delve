# Run inference on the production-line devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras need defect detection where network access is often unavailable. Inference must therefore work locally on each device.

## Decision Drivers

* Intermittent connectivity
* Camera-line inspection

## Considered Options

* On-device inference
* Central inference service

## Decision Outcome

Chosen option: "On-device inference".

Local inference keeps inspection available during network outages, matching the stated operating conditions.

### Consequences

* Devices need compatible inference hardware and runtime.
* Model updates must reach devices separately.

## Pros and Cons of the Options

### On-device inference

* Good, because Works offline
* Good, because Low network dependence
* Bad, because Device compute limits
* Bad, because Per-device deployment

### Central inference service

* Good, because Centralized compute
* Good, because Simpler model hosting
* Bad, because Requires connectivity
* Bad, because Network adds latency
