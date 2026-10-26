# Where should defect inference run?

* System: On-device visual inspection

## Context and Problem Statement

Production cameras need defect detection, often without network access. The model must be available where images are captured.

## Decision Drivers

* Offline operation
* Production-line inspection

## Considered Options

* Run inference on each device
* Run inference in a central service

## Decision Outcome

Chosen option: "Run inference on each device".

Local inference keeps inspection available without network access and avoids depending on a central service for each image.

### Consequences

* Devices need compatible inference runtimes and compute.
* Model deployment must cover the device fleet.

## Pros and Cons of the Options

### Run inference on each device

* Good, because Works offline
* Good, because Local response
* Bad, because Device resource limits
* Bad, because Fleet deployment effort

### Run inference in a central service

* Good, because Centralized compute
* Good, because Simpler model hosting
* Bad, because Needs connectivity
* Bad, because Network adds delay
