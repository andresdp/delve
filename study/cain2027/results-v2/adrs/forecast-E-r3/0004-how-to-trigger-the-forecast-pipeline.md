# How to trigger the forecast pipeline

* System: Retail demand forecasting

## Context and Problem Statement

Demand is forecast weekly, and changes should not break that run. The design space includes scheduled and commit triggered pipeline runs (d:12).

## Decision Drivers

* Protect weekly run
* Production speed

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-commit trigger (`v:12.2`)
* On-demand trigger (`v:12.1`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

Protecting the weekly run decides the choice: schedule the production forecast to its required cadence, accepting that experiments may not run immediately. The chosen design point returned no warnings; its on-commit rival also returned no warnings, and neither had attesting sources.

### Consequences

* Set and maintain the weekly production schedule.
* Provide a separate controlled path for ad hoc experiments.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Protect weekly run: supports weekly cadence
* Bad, because Production speed: experiments may await schedule
* Sources: `d:12`, `v:12.3`

### On-commit trigger

* Good, because Production speed: starts work after changes
* Bad, because Protect weekly run: changes may trigger unintended runs
* Sources: `d:12`, `v:12.2`

### On-demand trigger

* Good, because Protect weekly run: run timing is controlled
* Bad, because Production speed: requires manual initiation
* Sources: `d:12`, `v:12.1`
