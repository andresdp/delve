# Where should inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras often lack network access, so defect detection must execute at the production line. The design space supports edge inference, while the remote service option assumes online connectivity.

## Decision Drivers

* Offline operation
* Low latency

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Offline operation decides the choice: edge inference keeps inspection available without a network. This gives up the operational simplicity of centralized model serving.

### Consequences

* Package and distribute model runtime to cameras.
* Plan for device-level model updates and rollback.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Offline operation: runs on device
* Good, because Low latency: avoids network round trip
* Bad, because Tight budget: distributes deployment work
* Sources: `s01_p06`, `s07_p01`, `s19_p11`

### Model-as-a-service deployment

* Good, because Small team: centralized model operations
* Good, because Low cost: shared serving infrastructure
* Bad, because Offline operation: requires connectivity
* Bad, because Low latency: network round trip
