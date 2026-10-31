# Rollback to previous model version

*How should rollout failures be handled?*

* System: On-device visual inspection

## Context and Problem Statement

A newly retrained model is pushed to production devices, where network access may be intermittent. A prior known-good version provides a recovery path.

## Decision Drivers

* Device rollout
* Offline operation
* Model reliability

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Keeping a previous version available provides a straightforward recovery choice if a rollout causes inspection problems (d:10, v:10.2).

### Consequences

* Devices need storage for the previous model.
* Rollout tooling must support version switching.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Recovery path
* Good, because Limits faulty rollout impact
* Bad, because Requires retained artifacts
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Compare versions concurrently
* Bad, because More device storage
* Bad, because More rollout complexity
* Sources: `d:10`, `v:10.1`
