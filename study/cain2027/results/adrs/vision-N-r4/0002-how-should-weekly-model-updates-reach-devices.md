# How should weekly model updates reach devices?

* System: On-device visual inspection

## Context and Problem Statement

Retraining happens weekly, and the resulting model must be pushed to devices that may be offline. Update delivery needs to tolerate delayed connectivity.

## Decision Drivers

* weekly retraining
* offline devices
* small team

## Considered Options

* Device-initiated download
* Central push to devices
* Removable-media distribution

## Decision Outcome

Chosen option: "Device-initiated download".

It supports unattended delivery when a device reconnects and avoids requiring every camera to be continuously reachable.

### Consequences

* Offline devices may miss a weekly update until they reconnect.
* A central service must host versioned model packages.

## Pros and Cons of the Options

### Device-initiated download

* Good, because uses outbound connectivity
* Good, because simple central hosting
* Bad, because updates wait for reconnection
* Bad, because device polling overhead

### Central push to devices

* Good, because prompt delivery when reachable
* Good, because central orchestration
* Bad, because requires reachable devices
* Bad, because more infrastructure

### Removable-media distribution

* Good, because works without network
* Good, because low server needs
* Bad, because manual handling
* Bad, because slower fleet rollout
