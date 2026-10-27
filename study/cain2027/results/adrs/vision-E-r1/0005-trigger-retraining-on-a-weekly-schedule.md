# Trigger retraining on a weekly schedule

* System: On-device visual inspection

## Context and Problem Statement

The brief calls for retraining every week from newly labelled images. A scheduled trigger makes that cadence explicit and predictable.

## Decision Drivers

* Weekly cadence
* Repeatable operation
* Small team

## Considered Options

* On-schedule trigger (`v:12.3`)
* On availability of new training data trigger (`v:12.4`)
* On-demand trigger (`v:12.1`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

A weekly schedule directly implements the requested retraining frequency; the checked combination has no warnings, though it is unattested in the design space (d:12, v:12.3).

### Consequences

* Track missed or failed scheduled runs.
* Define how late-arriving labels enter a run.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Matches weekly cadence
* Good, because Predictable execution
* Bad, because May run without new labels
* Bad, because Needs schedule monitoring
* Sources: `d:12`, `v:12.3`

### On availability of new training data trigger

* Good, because Runs when data arrives
* Good, because Avoids unnecessary runs
* Bad, because Data arrival may be irregular
* Bad, because May not enforce weekly cadence
* Sources: `d:12`, `v:12.4`

### On-demand trigger

* Good, because Simple manual control
* Good, because Useful for ad hoc runs
* Bad, because Relies on operator action
* Bad, because Cadence can be missed
* Sources: `d:12`, `v:12.1`
