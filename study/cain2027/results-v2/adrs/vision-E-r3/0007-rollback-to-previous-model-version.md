# Rollback to previous model version

*How should a deployed model be rolled back?*

* System: On-device visual inspection

## Context and Problem Statement

Models are pushed to devices and may need to be replaced if a release causes problems. Keeping a previous version available supports recovery, with storage and rollout overhead.

## Decision Drivers

* Offline operation
* Reliable inspection

## Considered Options

* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Reliable inspection decides for retaining a rollback path, giving up device storage and package management simplicity.

### Consequences

* Devices need access to a prior known-good artifact.
* Rollout and rollback state must be tracked per device.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Reliable inspection: supports recovery from a bad release
* Bad, because Offline operation: rollback packages must be available on devices
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Budget: keeps only one active version
* Bad, because Reliable inspection: recovery requires another deployment
* Sources: `d:10`, `v:10.3`
