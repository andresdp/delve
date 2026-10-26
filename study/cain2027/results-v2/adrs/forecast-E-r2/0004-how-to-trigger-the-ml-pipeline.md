# How to trigger the ML pipeline?

* System: Retail demand forecasting

## Context and Problem Statement

The system has a fixed weekly run and needs an efficient path to evaluate new model ideas. The design space includes scheduled and commit-based triggers (d:12).

## Decision Drivers

* Protect weekly run
* Ship model ideas quickly
* Reproduce any past week

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-commit trigger (`v:12.2`)
* On-demand trigger (`v:12.1`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

Protecting the weekly run decides the choice: schedule the recurring pipeline, giving up immediate end-to-end execution on each model change (d:12, v:12.3).

### Consequences

* Provide a separate way to run experiments outside the production schedule.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Protect weekly run: predictable cadence
* Bad, because Ship model ideas quickly: waits for schedule
* Sources: `d:12`, `v:12.3`

### On-commit trigger

* Good, because Ship model ideas quickly: starts on code or data change
* Bad, because Protect weekly run: changes may contend with scheduled work

### On-demand trigger

* Good, because Protect weekly run: explicit operator control
* Bad, because Small team: requires manual coordination
