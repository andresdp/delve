# Distribute releases through an update service with device-side staging

* System: On-device visual inspection

## Context and Problem Statement

Updated models must reach cameras that may be offline. A device needs a safe way to accept a release when it reconnects without interrupting inspection.

## Decision Drivers

* Network independence
* Weekly model updates
* Inspection continuity

## Considered Options

* Device-initiated update with staged activation
* Central server push with immediate replacement

## Decision Outcome

Chosen option: "Device-initiated update with staged activation".

Network independence decides the choice because devices cannot be assumed reachable at rollout time. Staging adds update logic and delays adoption on disconnected devices.

### Consequences

* Devices need local storage for staged releases.
* Update status may differ across devices until they reconnect.

## Pros and Cons of the Options

### Device-initiated update with staged activation

* Good, because Network independence: updates can wait until reconnect
* Good, because Inspection continuity: activate after local staging
* Bad, because Small team: needs update and state handling

### Central server push with immediate replacement

* Good, because Weekly model updates: direct rollout control
* Bad, because Network independence: unavailable while disconnected
* Bad, because Inspection continuity: replacement can interrupt inspection
