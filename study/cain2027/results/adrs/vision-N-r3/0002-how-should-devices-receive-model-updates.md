# How should devices receive model updates?

* System: On-device visual inspection

## Context and Problem Statement

Models are retrained weekly and pushed to production devices that may be offline.

## Decision Drivers

* Weekly retraining
* Offline devices
* Tight infrastructure budget

## Considered Options

* Direct device download from a central model store
* Managed device update service

## Decision Outcome

Chosen option: "Direct device download from a central model store".

A central store and device-initiated downloads provide a simple, low-cost path for weekly updates when devices regain connectivity.

### Consequences

* Updates arrive later on disconnected devices.
* The team must track which model version each device runs.

## Pros and Cons of the Options

### Direct device download from a central model store

* Good, because Few infrastructure components
* Good, because Straightforward distribution
* Bad, because Devices need store access
* Bad, because Offline updates are delayed

### Managed device update service

* Good, because Coordinates fleet rollout
* Good, because Can track update status
* Bad, because Additional service to operate
* Bad, because May raise infrastructure cost
