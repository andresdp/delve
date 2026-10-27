# Trigger forecasts on a schedule

* System: Retail demand forecasting

## Context and Problem Statement

The production forecast must run weekly, which maps directly to a scheduled pipeline trigger (d:12).

## Decision Drivers

* Weekly run
* Predictable operation

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-demand trigger (`v:12.1`)
* On-commit trigger (`v:12.2`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

A schedule makes the required weekly execution predictable; ad hoc and commit triggers can supplement it for reruns or changed inputs (d:12, v:12.3).

### Consequences

* Track completion and alert on missed runs.
* Provide a controlled rerun path for corrected inputs.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Matches weekly cadence
* Good, because Predictable execution
* Bad, because Requires schedule monitoring
* Bad, because May need manual reruns
* Sources: `d:12`, `v:12.3`

### On-demand trigger

* Good, because Allows controlled reruns
* Good, because Useful for ad hoc runs
* Bad, because Weekly run depends on operator
* Bad, because Easy to miss a run
* Sources: `d:12`, `v:12.1`

### On-commit trigger

* Good, because Runs after code or data changes
* Good, because Fits change driven workflows
* Bad, because Does not itself enforce weekly cadence
* Bad, because May run too often
* Sources: `d:12`, `v:12.2`
