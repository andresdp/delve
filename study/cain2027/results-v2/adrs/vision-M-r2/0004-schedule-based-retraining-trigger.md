# Schedule-based retraining trigger

*What should trigger model retraining?*

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies a weekly retraining cadence from newly labelled images. Monitoring data changes can help surface issues, but the retraining schedule is already explicit.

## Decision Drivers

* Weekly updates
* Small team
* Reliable inspection

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Automated retraining pipeline (`v:6.5`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

Weekly updates decide the choice because they directly match the requested cadence. This gives up immediate adaptation to drift; the design space describes drift monitoring, but the brief does not specify drift-triggered retraining.

### Consequences

* Run retraining on a weekly schedule using newly labelled images.
* Review model quality before deployment; the promotion criteria need a separate decision.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Weekly updates: matches the stated cadence
* Good, because Small team: predictable recurring process
* Bad, because Reliable inspection: may not respond immediately to quality changes
* Bad, because Small team: scheduled runs may use unchanged data
* Sources: `s02_p08`, `s06_p07`, `s06_p11`, `s20_p06`, `s20_p12`, `s22_p08`, `s24_p07`

### Automated retraining pipeline

* Good, because Small team: automates training execution
* Good, because Weekly updates: supports repeatable retraining
* Bad, because Reliable inspection: automation alone does not define promotion safety
* Bad, because Small team: pipeline adds operational complexity
