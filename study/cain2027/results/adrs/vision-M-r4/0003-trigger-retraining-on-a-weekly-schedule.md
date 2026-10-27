# Trigger retraining on a weekly schedule

* System: On-device visual inspection

## Context and Problem Statement

The team already retrains weekly from newly labelled images. A recurring trigger fits that process and avoids making the small team operate a more complex trigger system.

## Decision Drivers

* Weekly retraining
* Small team

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Manual retraining trigger (`v:6.14`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

The stated weekly cadence directly supports a scheduled trigger and reduces routine operator effort. Sources *Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2*, Google’s *MLOps: Continuous delivery and automation pipelines in machine learning*, and *MLOps Principles* describe schedule-based retraining (s02_p08, s06_p07, s22_p08).

### Consequences

* Run training weekly and account for label availability.
* Define handling for weeks with no new labelled images.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Matches weekly cadence
* Good, because Predictable workload
* Bad, because May train without new labels
* Bad, because May miss changes between runs
* Sources: `s02_p08`, `s06_p07`, `s22_p08`

### Manual retraining trigger

* Good, because Human controls each run
* Good, because Low trigger automation
* Bad, because Depends on staff availability
* Bad, because Adds recurring manual work
* Sources: `s06_p11`, `s19_p08`, `s22_p04`
