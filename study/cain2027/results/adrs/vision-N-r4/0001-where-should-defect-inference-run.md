# Where should defect inference run?

* System: On-device visual inspection

## Context and Problem Statement

Production cameras inspect defects, often without network access. Results must remain available during outages.

## Decision Drivers

* intermittent connectivity
* production-line inspection

## Considered Options

* On-device inference
* Central server inference

## Decision Outcome

Chosen option: "On-device inference".

The brief places the model on cameras and notes frequent lack of network access, favoring local inference.

### Consequences

* Each device needs compatible inference software and compute.
* Inspection can continue during network outages.

## Pros and Cons of the Options

### On-device inference

* Good, because works offline
* Good, because local response
* Bad, because device compute limits
* Bad, because fleet deployment effort

### Central server inference

* Good, because centralized compute
* Good, because simpler model management
* Bad, because requires connectivity
* Bad, because network latency
