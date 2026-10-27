# Rollback to previous model version

*How should model versions be deployed and recovered?*

* System: On-device visual inspection

## Context and Problem Statement

A new model is delivered weekly to devices that may be offline. The design space includes rollback to a previous version and running multiple versions in production.

## Decision Drivers

* weekly updates
* offline devices
* production defect detection

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Keeping a previous model available provides a straightforward recovery option when devices receive a problematic update. The checked combination had no warnings, but no attesting sources.

### Consequences

* Retain a known-good model on each device.
* Provide a way to switch back locally.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because recovery path after bad release
* Bad, because requires retained prior version
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because multiple versions available
* Bad, because more version management
* Sources: `d:10`, `v:10.1`
