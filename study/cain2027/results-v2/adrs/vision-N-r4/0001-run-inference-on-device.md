# Run inference on-device

* System: On-device visual inspection

## Context and Problem Statement

Production cameras need defect detection even when the network is unavailable. The brief gives no latency target, but offline operation is explicit.

## Decision Drivers

* Offline operation
* Low infrastructure cost
* Detection latency

## Considered Options

* On-device inference
* Cloud inference

## Decision Outcome

Chosen option: "On-device inference".

Offline operation decides the choice: inference must remain available without network access. This gives up the simpler hardware and centralized compute of cloud inference.

### Consequences

* Devices must have enough compute and storage for the model.
* Model runtime and hardware compatibility need management.

## Pros and Cons of the Options

### On-device inference

* Good, because Offline operation: works without network
* Good, because Infrastructure cost: avoids inference servers
* Bad, because Device cost: requires capable hardware

### Cloud inference

* Good, because Device cost: simpler cameras
* Bad, because Offline operation: unavailable without network
* Bad, because Detection latency: adds network round trip
