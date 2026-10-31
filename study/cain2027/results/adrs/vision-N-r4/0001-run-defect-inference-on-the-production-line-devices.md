# Run defect inference on the production-line devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras may lack network access, so defect checks must work locally. The brief does not specify device hardware or latency targets.

## Decision Drivers

* Offline operation
* Line-side inspection

## Considered Options

* On-device inference
* Central server inference

## Decision Outcome

Chosen option: "On-device inference".

Local inference keeps inspection available without a network connection, which is a stated operating condition. Device capacity must be verified against the selected model.

### Consequences

* Models must fit device resources.
* Inspection can continue during outages.

## Pros and Cons of the Options

### On-device inference

* Good, because Works offline
* Good, because Low network dependence
* Bad, because Device resource limits
* Bad, because Fleet deployment work

### Central server inference

* Good, because Centralized compute
* Good, because Simpler model management
* Bad, because Requires connectivity
* Bad, because Network adds latency
