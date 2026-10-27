# Push versioned model packages to devices

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must reach cameras along production lines, including devices that are often offline. Versioning supports identifying which model is deployed and returning to a prior release.

## Decision Drivers

* Weekly model delivery
* Often offline
* Tight budget

## Considered Options

* Versioned package distribution
* Direct replacement of model files

## Decision Outcome

Chosen option: "Versioned package distribution".

A versioned package makes each weekly model identifiable and allows devices to update when reachable. It also gives the team a practical path to revert a bad release.

### Consequences

* Devices may run different model versions temporarily.
* Packages need version and compatibility metadata.

## Pros and Cons of the Options

### Versioned package distribution

* Good, because Supports staged delivery
* Good, because Enables rollback
* Bad, because Needs package management
* Bad, because Offline devices update later

### Direct replacement of model files

* Good, because Minimal tooling
* Good, because Simple transfer
* Bad, because Weak rollback support
* Bad, because Partial updates risk failure
