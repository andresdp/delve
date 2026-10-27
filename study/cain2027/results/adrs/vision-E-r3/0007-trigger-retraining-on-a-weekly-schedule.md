# Trigger retraining on a weekly schedule

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies weekly retraining, so a scheduled trigger directly matches the requested operating cadence.

## Decision Drivers

* Weekly retraining
* Small team

## Considered Options

* On-schedule trigger (`v:12.3`)
* On availability of new training data trigger (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

A weekly schedule follows the explicit requirement and keeps retraining behavior predictable (d:12, v:12.3).

### Consequences

* Handle weeks when new labels are missing or incomplete.
* Keep training execution separate from device connectivity.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Matches cadence
* Good, because Predictable operations
* Bad, because May run without new data
* Sources: `d:12`, `v:12.3`

### On availability of new training data trigger

* Good, because Runs when data arrives
* Bad, because Does not enforce weekly cadence
* Sources: `d:12`, `v:12.4`
