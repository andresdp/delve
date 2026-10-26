# How should the pipeline be triggered?

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts are produced weekly, so the production run needs a predictable trigger.

## Decision Drivers

* Weekly cadence
* Reliable execution

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-demand trigger (`v:12.1`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

A scheduled trigger directly matches the weekly forecast requirement and reduces reliance on manual execution (d:12, v:12.3).

### Consequences

* Schedule failures need detection.
* Ad hoc reruns need a separate trigger path.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Predictable weekly runs
* Good, because Automates routine execution
* Bad, because Schedule needs maintenance
* Sources: `d:12`, `v:12.3`

### On-demand trigger

* Good, because Flexible run timing
* Bad, because Relies on manual action
* Sources: `d:12`, `v:12.1`
