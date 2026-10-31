# Validate models before promoting them to production

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces candidate models, and pushing every candidate directly to production risks degrading defect detection. The brief gives no acceptance criteria, so validation can be chosen without specifying thresholds.

## Decision Drivers

* Weekly model changes
* Defect detection

## Considered Options

* Validate before promotion
* Deploy each training output

## Decision Outcome

Chosen option: "Validate before promotion".

A validation gate reduces the chance that an unreviewed weekly model change reaches production devices.

### Consequences

* The team must define validation data and acceptance criteria.
* Promotion adds a step to each weekly release.

## Pros and Cons of the Options

### Validate before promotion

* Good, because Screens candidate regressions
* Good, because Separates training from release
* Bad, because Adds release work
* Bad, because Needs validation data

### Deploy each training output

* Good, because Fastest release path
* Good, because Minimal process
* Bad, because Regressions reach devices
* Bad, because No promotion gate
