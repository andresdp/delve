# Run defect inference on the production-line devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras may lack network access, but inspection must continue at the line. The brief calls for the model to run on those devices.

## Decision Drivers

* Network-independent inspection
* Production-line cameras

## Considered Options

* On-device inference
* Central server inference

## Decision Outcome

Chosen option: "On-device inference".

Local inference lets inspection continue without network access and matches the brief’s camera-based deployment.

### Consequences

* Models must fit device resources
* Inference software must be deployed to devices

## Pros and Cons of the Options

### On-device inference

* Good, because Works offline
* Good, because Low network dependence
* Bad, because Device resource limits

### Central server inference

* Good, because Centralized compute
* Bad, because Requires connectivity
* Bad, because Adds network latency
