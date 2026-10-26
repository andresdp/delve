# Production model version strategy

* System: On-device visual inspection

## Context and Problem Statement

Models are pushed to multiple devices and a bad weekly release could affect defect detection across the line.

## Decision Drivers

* Safe releases
* Offline devices
* Reproducibility

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Safe releases decide the choice: preserve and redeploy the previous model if the candidate underperforms. Recovery is delayed for disconnected devices.

### Consequences

* Retain a known-good model artifact on each device.
* Track which version each device is running.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Safe releases: supports recovery from a bad model
* Bad, because Offline devices: rollback waits for device connectivity
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Safe releases: enables parallel model versions
* Bad, because Tight budget: increases storage and rollout complexity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Tight budget: simplest deployment state
* Bad, because Safe releases: no explicit previous-version recovery
* Sources: `d:10`, `v:10.3`
