# On-schedule trigger

*How should weekly retraining be triggered?*

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for regular retraining, so training should run on a predictable cadence.

## Decision Drivers

* Weekly updates
* Reproducibility
* Tight budget

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-demand trigger (`v:12.1`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

Weekly updates decide the choice: scheduled runs match the stated retraining cadence. This gives up avoiding runs when no new labels are available. The design space has no source passages; this choice is grounded in d:12 and v:12.3.

### Consequences

* A scheduler starts weekly training.
* Training data availability needs checking.
* Runs are easy to anticipate.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Weekly updates: matches a regular cadence
* Good, because Reproducibility: predictable run timing
* Bad, because Tight budget: scheduled runs may occur without new labels
* Sources: `d:12`, `v:12.3`

### On-demand trigger

* Good, because Tight budget: run only when requested
* Bad, because Weekly updates: requires manual action
* Bad, because Reproducibility: timing can vary
* Sources: `d:12`, `v:12.1`
