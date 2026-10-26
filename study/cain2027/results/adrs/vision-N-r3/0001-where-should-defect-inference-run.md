# Where should defect inference run?

* System: On-device visual inspection

## Context and Problem Statement

Production cameras may have no network access, so inspection must continue locally.

## Decision Drivers

* Offline operation
* Line-side inspection
* Small team

## Considered Options

* On-device inference
* Central server inference

## Decision Outcome

Chosen option: "On-device inference".

Local inference keeps inspection available without network access and avoids sending each image to a server.

### Consequences

* Devices need enough compute for the model.
* Inference software must be deployed and maintained across the fleet.

## Pros and Cons of the Options

### On-device inference

* Good, because Works offline
* Good, because Low network load
* Bad, because Device compute limits
* Bad, because Fleet hardware needs management

### Central server inference

* Good, because Centralized compute
* Good, because Simpler model hardware
* Bad, because Requires connectivity
* Bad, because Network adds latency
