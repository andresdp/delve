# What triggers the training pipeline?

* System: On-device visual inspection

## Context and Problem Statement

A weekly retraining cadence calls for a predictable pipeline trigger. Scheduled runs are one of the design space alternatives (d:12).

## Decision Drivers

* Weekly cadence
* Predictable operations
* Small team

## Considered Options

* On-schedule trigger (`v:12.3`)
* On availability of new training data trigger (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

A scheduled trigger matches the explicit weekly retraining requirement and gives the small team a regular operating cadence (d:12, v:12.3).

### Consequences

* The pipeline must check that newly labelled images are available.
* Missed runs need an operational recovery path.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Predictable weekly runs
* Good, because Simple operating rhythm
* Bad, because May run without useful new data
* Bad, because Data readiness must be managed
* Sources: `d:12`, `v:12.3`

### On availability of new training data trigger

* Good, because Runs when data is ready
* Good, because Avoids empty runs
* Bad, because Needs reliable data eventing
* Bad, because Timing may vary
* Sources: `d:12`, `v:12.4`
