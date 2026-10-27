# Automate weekly retraining from new labels

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly using newly labelled images, which calls for a repeatable training workflow and a clear trigger.

## Decision Drivers

* Weekly cadence
* New labels
* Small team

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Performance- or drift-based retraining trigger (`v:6.8`)
* Manual retraining trigger (`v:6.14`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

The brief specifies weekly retraining, and the design space supports recurring schedule-based starts. A drift trigger could complement the schedule if monitoring is later added, but it does not replace the required cadence.

### Consequences

* Run the training workflow weekly.
* Define behavior for weeks with no new labels.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Matches weekly cadence
* Good, because Predictable runs
* Bad, because May run without useful new data
* Sources: `s02_p08`, `s06_p07`, `s22_p08`

### Performance- or drift-based retraining trigger

* Good, because Responds to degradation
* Good, because Uses drift signals
* Bad, because Requires monitoring thresholds
* Bad, because Less predictable cadence
* Sources: `s06_p08`, `s20_p06`, `s22_p15`

### Manual retraining trigger

* Good, because Human control
* Good, because Simple trigger
* Bad, because Adds team workload
* Bad, because Can miss cadence
* Sources: `s20_p06`
