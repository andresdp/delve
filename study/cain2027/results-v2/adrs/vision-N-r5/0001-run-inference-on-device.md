# Run inference on-device

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect production-line images where network access is often unavailable. The detection path must still work locally.

## Decision Drivers

* Network independence
* Inspection latency
* Infrastructure cost

## Considered Options

* On-device inference
* Central inference service

## Decision Outcome

Chosen option: "On-device inference".

Network independence decides the choice because inspections must work without connectivity. This gives up simpler centralized runtime management and requires capable devices.

### Consequences

* Each device needs suitable compute and local model storage.
* Inference can continue during network outages.

## Pros and Cons of the Options

### On-device inference

* Good, because Network independence: operates offline
* Good, because Inspection latency: avoids round trip
* Bad, because Infrastructure cost: devices need compute
* Bad, because Small team: device fleet to support

### Central inference service

* Good, because Small team: centralized runtime
* Bad, because Network independence: requires connectivity
* Bad, because Inspection latency: adds network delay
