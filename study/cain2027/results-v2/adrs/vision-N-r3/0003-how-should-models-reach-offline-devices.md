# How should models reach offline devices?

* System: On-device visual inspection

## Context and Problem Statement

Updated models must reach production devices weekly even though network access is often unavailable. Devices need a way to receive updates when connectivity returns.

## Decision Drivers

* Offline availability
* Weekly freshness
* Reproducibility

## Considered Options

* Versioned update packages with device polling
* Removable-media updates
* Continuous network streaming

## Decision Outcome

Chosen option: "Versioned update packages with device polling".

Reproducibility decides the choice: each device can report and receive a clearly identified model release. This gives up immediate freshness when a device is offline; it updates after connectivity returns.

### Consequences

* Track the model version installed on each device.
* Allow update delay to vary with device connectivity.

## Pros and Cons of the Options

### Versioned update packages with device polling

* Good, because Weekly freshness: devices fetch available releases
* Good, because Reproducibility: package identifies model version
* Bad, because Offline availability: updates wait for connectivity

### Removable-media updates

* Good, because Offline availability: no network required
* Good, because Low cost: uses simple transfer media
* Bad, because Weekly freshness: manual distribution slows updates
* Bad, because Reproducibility: handling can vary

### Continuous network streaming

* Good, because Weekly freshness: updates can arrive promptly
* Bad, because Offline availability: requires a stable connection
* Bad, because Low cost: adds always-on service needs
