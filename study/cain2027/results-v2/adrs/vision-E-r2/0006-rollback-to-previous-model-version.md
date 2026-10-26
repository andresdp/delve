# Rollback to previous model version

*How should production model versions be managed?*

* System: On-device visual inspection

## Context and Problem Statement

New models are delivered weekly to production devices. Defect detection needs a recovery path if a new release performs poorly.

## Decision Drivers

* Reliable production
* Weekly delivery
* Tight budget

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Reliable production decides the choice: retaining a previous model enables recovery after a bad weekly release. This costs artifact storage and device delivery capacity.

### Consequences

* Keep a known prior model artifact available for each device.
* Define an operational rollback procedure.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Reliable production: supports recovery to a prior model
* Bad, because Tight budget: requires retaining and distributing prior artifacts
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Reliable production: supports concurrent model versions
* Bad, because Tight budget: more storage and release coordination
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Tight budget: simplest active model state
* Bad, because Reliable production: no explicit prior-version recovery path
* Sources: `d:10`, `v:10.3`
