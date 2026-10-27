# Keep inspection operational when model updates are unavailable

* System: On-device visual inspection

## Context and Problem Statement

Devices often lack network access, so updates cannot be assumed to arrive on schedule. Each device needs a usable local model between releases.

## Decision Drivers

* Offline operation
* Weekly updates
* Continuous inspection

## Considered Options

* Retain the current local model until replacement
* Require an update before inspection

## Decision Outcome

Chosen option: "Retain the current local model until replacement".

Keeping the installed model available preserves inspection during outages and allows updates to wait for connectivity.

### Consequences

* Devices can temporarily run different model versions.
* The team must define how long older versions remain acceptable.

## Pros and Cons of the Options

### Retain the current local model until replacement

* Good, because Inspection continues offline
* Good, because Update timing is flexible
* Bad, because Some devices use older models
* Bad, because Requires local storage

### Require an update before inspection

* Good, because Keeps versions aligned
* Good, because Avoids stale models
* Bad, because Outages stop inspection
* Bad, because Requires reliable connectivity
