# Where should defect inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect production lines that often lack network access. Priority requirements: offline inspection, weekly model freshness, reproducibility, low cost, and small-team operability.

## Decision Drivers

* Offline availability
* Low latency
* Low cost

## Considered Options

* On-device inference
* Central inference service
* Hybrid local and remote inference

## Decision Outcome

Chosen option: "On-device inference".

Offline availability decides the choice: inference must continue when the network is unavailable. This gives up the economies of shared compute and requires capable devices.

### Consequences

* Provision devices with suitable inference hardware.
* Keep the inspection path independent of network services.

## Pros and Cons of the Options

### On-device inference

* Good, because Offline availability: works without network
* Good, because Low latency: local inference
* Bad, because Low cost: devices need compute capacity

### Central inference service

* Good, because Low cost: shared compute
* Bad, because Offline availability: requires connectivity
* Bad, because Low latency: network round trip

### Hybrid local and remote inference

* Good, because Offline availability: local fallback
* Good, because Low cost: remote capacity can be shared
* Bad, because Low cost: duplicates infrastructure
* Bad, because Offline availability: behavior can vary by connection
