# On-schedule trigger

*How should the forecast pipeline be triggered?*

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly forecasts, so it needs a recurring trigger. The design space includes scheduled execution. [d:12, v:12.3]

## Decision Drivers

* Weekly forecast cadence
* Reliable run

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-demand trigger (`v:12.1`)
* On-availability-of-new-training-data trigger (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

A schedule provides the regular weekly execution the brief requires; ad hoc reruns can still be initiated as needed. [d:12, v:12.3]

### Consequences

* The schedule and run status need operational ownership.
* Past weeks can be rerun on demand.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Matches weekly cadence
* Good, because Predictable execution
* Bad, because Schedule failures need handling
* Sources: `d:12`, `v:12.3`

### On-demand trigger

* Good, because Supports ad hoc reruns
* Bad, because Weekly run depends on manual action
* Sources: `d:12`, `v:12.1`

### On-availability-of-new-training-data trigger

* Good, because Runs when data arrives
* Bad, because Arrival timing may vary
* Sources: `d:12`, `v:12.4`
