# Run defect detection on the production-line devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras need defect decisions even when network access is unavailable. The brief places the model at the cameras but does not specify where inference runs.

## Decision Drivers

* Offline operation
* Line-side inspection

## Considered Options

* On-device inference
* Centralized inference

## Decision Outcome

Chosen option: "On-device inference".

Local inference meets the offline requirement and keeps inspection close to the cameras.

### Consequences

* Devices need a compatible inference runtime.
* Model size and compute use constrain deployment.

## Pros and Cons of the Options

### On-device inference

* Good, because Works offline
* Good, because Low response latency
* Bad, because Limited device resources
* Bad, because Requires device deployment

### Centralized inference

* Good, because Central compute capacity
* Good, because Simpler model updates
* Bad, because Requires network access
* Bad, because Adds response latency
