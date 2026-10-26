# Model release testing

* System: On-device visual inspection

## Context and Problem Statement

Each weekly retraining produces a candidate model that must be checked before distribution to production cameras.

## Decision Drivers

* Defect detection quality
* Weekly releases
* Tight budget

## Considered Options

* Testing trained model quality (`v:26.9`)
* Canary testing (`v:26.1`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Defect detection quality decides the choice: evaluate each candidate against labelled examples before deployment. This costs evaluation data and weekly review time.

### Consequences

* Maintain a representative labelled evaluation set.
* Block release when candidate quality misses agreed thresholds.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Defect detection quality: gates on model results
* Bad, because Weekly releases: requires representative labelled evaluation data
* Sources: `d:26`, `v:26.9`

### Canary testing

* Good, because Safe releases: limits initial exposure
* Bad, because Offline devices: staged rollout may take time
* Sources: `d:26`, `v:26.1`

### No testing

* Good, because Tight budget: avoids test work
* Bad, because Defect detection quality: bad models may ship
* Sources: `d:26`, `v:26.14`
