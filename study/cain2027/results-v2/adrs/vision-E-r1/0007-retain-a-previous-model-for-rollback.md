# Retain a previous model for rollback

* System: On-device visual inspection

## Context and Problem Statement

A new model is pushed to production devices after retraining, and the brief gives no guarantee of network access during recovery. The design space includes rollback to a previous version (d:10).

## Decision Drivers

* Offline inference
* Weekly retraining

## Considered Options

* Rollback to previous model version (`v:10.2`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Offline inference decides the choice: keeping a previous model available allows local recovery if a release fails. This costs device storage and rollout handling.

### Consequences

* Keep the previous model available on each device.
* Define a local switch-back procedure.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Offline inference: supports local recovery
* Bad, because Small team and tight budget: retains model copies
* Sources: `d:10`, `v:10.2`

### Single model in production

* Good, because Cost: uses less device storage
* Bad, because Offline inference: no local fallback model
* Sources: `d:10`, `v:10.3`
