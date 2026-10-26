# What should trigger the forecasting pipeline?

* System: Retail demand forecasting

## Context and Problem Statement

The system needs a repeatable weekly run, while model ideas should also be testable and deliverable without disrupting that run.

## Decision Drivers

* Weekly schedule
* Fast model iteration
* Reliable production run

## Considered Options

* On-schedule trigger (`v:12.3`)
* On-commit trigger (`v:12.2`)
* On availability of new training data trigger (`v:12.4`)

## Decision Outcome

Chosen option: "On-schedule trigger" (`v:12.3`).

A weekly schedule matches the stated forecast interval; use separate development and delivery automation for rapid model iteration. The checked combination had no warnings and no attested sources.

### Consequences

* A weekly run occurs independently of code changes.
* The schedule and input cutoff need to be recorded.

## Pros and Cons of the Options

### On-schedule trigger

* Good, because Matches weekly cadence
* Good, because Predictable execution
* Bad, because Requires schedule management
* Sources: `d:12`, `v:12.3`

### On-commit trigger

* Good, because Fast feedback on changes
* Bad, because Commits can trigger unscheduled runs
* Sources: `d:12`, `v:12.2`

### On availability of new training data trigger

* Good, because Runs when data arrives
* Bad, because Data arrival may not match weekly cadence
* Sources: `d:12`, `v:12.4`
