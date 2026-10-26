# Downloadable signed model packages

*How should model updates reach devices?*

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must be pushed to production devices that may lack network access. The brief does not specify how often devices reconnect.

## Decision Drivers

* Offline operation
* Weekly retraining
* Small team

## Considered Options

* Direct online push
* Downloadable signed model packages
* Removable-media deployment

## Decision Outcome

Chosen option: "Downloadable signed model packages".

Offline operation decides the choice: versioned packages can be installed when devices reconnect or via local transfer. This gives up the simplicity of a direct online push and adds package handling.

### Consequences

* Devices need a process to verify and install packages.
* A release needs a stable model version identifier.

## Pros and Cons of the Options

### Direct online push

* Good, because Weekly retraining: fast delivery when connected
* Good, because Small team: straightforward distribution path
* Bad, because Offline operation: cannot reach disconnected devices

### Downloadable signed model packages

* Good, because Offline operation: packages can be transferred after reconnection
* Good, because Weekly retraining: supports versioned releases
* Bad, because Small team: package and device update handling

### Removable-media deployment

* Good, because Offline operation: works without network access
* Bad, because Small team: manual distribution effort
* Bad, because Weekly retraining: slower fleet-wide delivery
