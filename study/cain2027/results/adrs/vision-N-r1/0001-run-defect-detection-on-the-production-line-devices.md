# Run defect detection on the production-line devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect products where network access is often unavailable. Defect detection must continue during network outages.

## Decision Drivers

* Offline operation
* Line-side inspection

## Considered Options

* On-device inference
* Cloud inference

## Decision Outcome

Chosen option: "On-device inference".

Local inference keeps inspection available without network access and avoids a network round trip for each image.

### Consequences

* Devices need sufficient compute and storage.
* The team must manage model versions across devices.

## Pros and Cons of the Options

### On-device inference

* Good, because Works offline
* Good, because Low network latency
* Bad, because Device compute limits
* Bad, because Fleet deployment effort

### Cloud inference

* Good, because Centralized compute
* Good, because Simpler model updates
* Bad, because Requires connectivity
* Bad, because Adds network latency
