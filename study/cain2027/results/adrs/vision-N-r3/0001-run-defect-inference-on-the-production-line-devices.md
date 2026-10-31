# Run defect inference on the production-line devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras operate along production lines that often lack network access. Defect detection must remain available when connectivity is unavailable.

## Decision Drivers

* Offline operation
* Production-line inspection

## Considered Options

* On-device inference
* Centralized inference service

## Decision Outcome

Chosen option: "On-device inference".

Local inference supports inspection during network outages and avoids dependence on a central service for each image.

### Consequences

* Devices need adequate compute and storage.
* Inference software must be maintained across the fleet.

## Pros and Cons of the Options

### On-device inference

* Good, because Works offline
* Good, because Low network demand
* Bad, because Device compute limits
* Bad, because Fleet deployment effort

### Centralized inference service

* Good, because Centralized compute
* Good, because Simpler model hosting
* Bad, because Requires connectivity
* Bad, because Adds network dependency
