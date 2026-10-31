# Package and distribute versioned model releases to devices

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must reach cameras that may not have network access. A release package provides a unit that can be transferred and installed when a device is reachable.

## Decision Drivers

* Weekly model push
* Intermittent connectivity
* Small team

## Considered Options

* Versioned model packages
* Live model delivery

## Decision Outcome

Chosen option: "Versioned model packages".

Versioned packages allow models to be transferred and installed despite intermittent connectivity, while making releases identifiable.

### Consequences

* Devices need a package installation mechanism.
* Release versions must be tracked across devices.

## Pros and Cons of the Options

### Versioned model packages

* Good, because Supports offline transfer
* Good, because Identifiable releases
* Bad, because Requires installation process
* Bad, because Package compatibility matters

### Live model delivery

* Good, because Automated when connected
* Good, because Centralized delivery
* Bad, because Needs network access
* Bad, because Unreachable devices lag
