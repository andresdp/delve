# Keep the previous model available for rollback

* System: On-device visual inspection

## Context and Problem Statement

A new model is pushed to production devices weekly. The brief does not define an online recovery path for cameras that may be disconnected.

## Decision Drivers

* Production inspection
* Intermittent connectivity
* Weekly model releases

## Considered Options

* Retain a known-good local model
* Reinstall from a central service

## Decision Outcome

Chosen option: "Retain a known-good local model".

Keeping the prior model on-device supports recovery even when network access is unavailable.

### Consequences

* Devices need space for multiple model versions
* Rollback behavior needs implementation

## Pros and Cons of the Options

### Retain a known-good local model

* Good, because Offline rollback
* Good, because Limits outage duration
* Bad, because Uses device storage

### Reinstall from a central service

* Good, because One recovery source
* Bad, because Requires connectivity
* Bad, because Recovery may be delayed
