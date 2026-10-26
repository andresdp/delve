# How should weekly models reach devices?

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly and needs to reach cameras that may be offline when an update is published.

## Decision Drivers

* Weekly retraining
* Intermittent connectivity
* Small team

## Considered Options

* Devices pull versioned releases when connected
* Push each release to all devices

## Decision Outcome

Chosen option: "Devices pull versioned releases when connected".

A versioned pull model accommodates devices that reconnect at different times while keeping releases centrally managed.

### Consequences

* Devices need to track installed and available versions.
* Some devices may remain on older models while offline.

## Pros and Cons of the Options

### Devices pull versioned releases when connected

* Good, because Fits intermittent access
* Good, because Central release point
* Bad, because Update timing varies
* Bad, because Requires device updater

### Push each release to all devices

* Good, because Coordinated rollout
* Good, because Central control
* Bad, because Needs connectivity
* Bad, because Offline devices miss updates
