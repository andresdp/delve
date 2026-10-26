# How should retraining start?

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labelled images. The system needs a repeatable way to start that work.

## Decision Drivers

* Weekly retraining cadence
* Small team
* New labelled images

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Performance- or drift-based retraining trigger (`v:6.8`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

The stated weekly cadence decides the choice: schedule retraining weekly, gated on the new labels being available. This gives up automatic response to drift between runs; the design space also supports automated retraining, with evidence in MLOps: Continuous delivery and automation pipelines in machine learning.

### Consequences

* Make label availability a prerequisite for each scheduled run.
* Budget for retraining even when model quality has not changed.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Weekly cadence: directly supports recurring runs
* Good, because Small team: avoids manual run initiation
* Bad, because New labels: schedule may run before data is ready
* Bad, because Model quality: schedule alone does not detect degradation
* Sources: `s02_p08`, `s06_p07`, `s06_p11`, `s20_p06`, `s22_p08`

### Performance- or drift-based retraining trigger

* Good, because Model quality: can react to degradation or drift
* Good, because Compute cost: can avoid unnecessary scheduled runs
* Bad, because Weekly cadence: does not ensure weekly training
* Bad, because Small team: requires monitoring and trigger maintenance
