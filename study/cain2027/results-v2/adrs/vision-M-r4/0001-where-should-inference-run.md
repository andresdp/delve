# Where should inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras must detect defects while production lines may have no network access. The brief gives no specific latency target.

## Decision Drivers

* Disconnected operation
* On-device inspection
* Tight infrastructure budget

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Disconnected operation decides the choice: inference stays available without a network connection. This gives up the simpler central model rollout of a service; the evidence supports edge placement but does not establish its cost or device requirements.

### Consequences

* Plan a reliable way to distribute model updates to devices.
* Validate inference performance and resource use on target hardware.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Disconnected operation: inference runs on the device
* Good, because Infrastructure cost: avoids a continuous serving service
* Bad, because Deployment effort: distribute models to devices
* Bad, because Device capacity: constrained by local hardware
* Sources: `s07_p01`, `s19_p11`, `s25_p07`

### Model-as-a-service deployment

* Good, because Model updates: central serving simplifies rollout
* Good, because Device capacity: inference uses server resources
* Bad, because Disconnected operation: requires network access
* Bad, because Infrastructure cost: requires serving infrastructure
