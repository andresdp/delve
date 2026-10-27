# Distribute model updates to devices

* System: On-device visual inspection

## Context and Problem Statement

Retrained models are pushed to devices, although those devices often lack network access. The update mechanism must tolerate devices being unreachable during a release.

## Decision Drivers

* Push models to devices
* Intermittent connectivity
* Small team

## Considered Options

* Direct network push with retry
* Removable-media transfer

## Decision Outcome

Chosen option: "Direct network push with retry".

Push is the stated delivery approach; retrying allows disconnected devices to receive updates when connectivity returns.

### Consequences

* Devices need a mechanism to check for and install pending updates.
* Rollout completion can lag the weekly training cadence.

## Pros and Cons of the Options

### Direct network push with retry

* Good, because Automated delivery
* Good, because No manual media handling
* Bad, because Needs eventual connectivity
* Bad, because Requires retry tracking

### Removable-media transfer

* Good, because Works without network
* Good, because Low service infrastructure
* Bad, because Manual fleet work
* Bad, because Slower rollout
