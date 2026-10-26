# Schedule-based retraining trigger

*How should retraining be triggered?*

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for weekly retraining. The design space treats schedule-based retraining and data or performance triggers as practices that may be combined, rather than mutually exclusive alternatives.

## Decision Drivers

* Weekly cadence
* Label availability
* Small team

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Threshold-based retraining (`v:6.3`)
* Manual retraining trigger (`v:6.14`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

The stated weekly cadence decides the choice: schedule retraining to match it and gate training on the availability of newly labelled images. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “MLOps: Continuous delivery and automation pipelines in machine learning” describe recurring triggers; this gives up reacting immediately to drift between runs.

### Consequences

* Skip or defer scheduled runs when new labels are unavailable.
* Changes in image quality may remain undetected until the next run.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Weekly cadence: predictable recurring runs
* Bad, because Label availability: may run without useful new labels
* Sources: `s02_p08`, `s06_p11`

### Threshold-based retraining

* Good, because Label availability: can react to quality changes
* Bad, because Small team: thresholds need tuning and oversight
* Sources: `s06_p08`, `s09_p03`

### Manual retraining trigger

* Good, because Small team: direct human control
* Bad, because Weekly cadence: recurring operator effort
