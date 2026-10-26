# What to validate before releasing a model?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining creates candidate models that will be used for defect detection on production lines. The release path needs a quality gate.

## Decision Drivers

* Defect detection
* Weekly model builds
* Production use

## Considered Options

* Testing trained model quality (`v:26.9`)
* Canary testing (`v:26.1`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Model quality testing gives the weekly build a release check relevant to defect detection. The design point has no warnings, but no attesting sources.

### Consequences

* Define an acceptance measure for candidate models.
* Hold deployment when a candidate misses the quality bar.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Checks candidate model quality
* Bad, because Needs a quality threshold
* Sources: `d:26`, `v:26.9`

### Canary testing

* Good, because Limits initial rollout exposure
* Bad, because Needs staged device rollout
* Sources: `d:26`, `v:26.1`

### No testing

* Good, because No test setup
* Bad, because Unmeasured release quality
* Sources: `d:26`, `v:26.14`
