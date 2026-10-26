# What should trigger retraining?

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies a weekly retraining rhythm. A scheduled trigger matches that cadence without needing devices to report new data or performance over a network.

## Decision Drivers

* Weekly retraining
* Offline operation
* Small team

## Considered Options

* On-schedule trigger (`v:12.3`)
* On availability of new training data trigger (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

The specified weekly cadence decides for a schedule, trading immediate response to new data for a predictable, simple trigger.

### Consequences

* Missed runs need detection and recovery.
* Label arrival timing may delay retraining until the next scheduled run.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Weekly retraining: matches a fixed cadence
* Bad, because Small team: schedule and failures need oversight
* Sources: `d:12`, `v:12.3`

### On availability of new training data trigger

* Good, because Weekly retraining: reacts when new images arrive
* Bad, because Offline operation: depends on data availability signals
* Sources: `d:12`, `v:12.4`
