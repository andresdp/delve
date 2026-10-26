# Trigger the weekly forecast pipeline

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly demand forecasts, so its main pipeline needs a recurring trigger. The design space includes scheduled and manual triggers.

## Decision Drivers

* 1. Protect weekly run
* 2. Small team

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-demand trigger (`v:12.1`)
* On availability of new training data trigger (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

Protecting the weekly run decides the choice: a scheduled trigger directly matches the required cadence. The trade-off is that missed or failed runs need handling that the brief does not define.

### Consequences

* Configure a recurring weekly run.
* Specify monitoring and recovery for missed or failed runs.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Weekly run: runs on a recurring cadence
* Bad, because Protect weekly run: requires failure handling
* Sources: `d:12`, `v:12.3`

### On-demand trigger

* Good, because Small team: simple to start manually
* Bad, because Weekly run: depends on an operator to remember
* Sources: `d:12`, `v:12.1`

### On availability of new training data trigger

* Good, because Weekly run: reacts when data arrives
* Bad, because Protect weekly run: arrival may not match weekly cadence
* Sources: `d:12`, `v:12.4`
