# Trigger retraining weekly

* System: On-device visual inspection

## Context and Problem Statement

The brief explicitly sets a weekly retraining cadence from newly labeled images. The design space includes scheduled and new-data triggers (d:12).

## Decision Drivers

* Weekly retraining
* Small team and tight budget

## Considered Options

* On-schedule trigger (`v:12.3`)
* On availability of new training data trigger (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

The stated weekly cadence decides the choice: a schedule is simple and predictable. It can wait until the next run when labels arrive just after a run.

### Consequences

* Configure the schedule for weekly execution.
* Ensure each run uses the latest available labeled images.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Weekly retraining: matches stated cadence
* Good, because Small team: predictable operation
* Bad, because Weekly retraining: may wait for new labels
* Sources: `d:12`, `v:12.3`

### On availability of new training data trigger

* Good, because Weekly retraining: reacts when labels arrive
* Bad, because Small team: needs reliable data event handling
* Sources: `d:12`, `v:12.4`
