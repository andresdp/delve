# How should forecasting run?

* System: Retail demand forecasting

## Context and Problem Statement

The system must produce weekly forecasts for each store and product. The brief does not specify whether the run is scheduled or event-driven.

## Decision Drivers

* Weekly forecasts
* Three-person team

## Considered Options

* Scheduled batch pipeline
* Event-driven pipeline

## Decision Outcome

Chosen option: "Scheduled batch pipeline".

A scheduled batch run matches the weekly forecast cadence and keeps operational overhead low for a small team.

### Consequences

* Requires a reliable scheduler.
* Late inputs need a defined handling policy.

## Pros and Cons of the Options

### Scheduled batch pipeline

* Good, because Fits weekly cadence
* Good, because Simple operations
* Bad, because Waits for schedule
* Bad, because Needs run monitoring

### Event-driven pipeline

* Good, because Runs on new data
* Good, because Flexible timing
* Bad, because More moving parts
* Bad, because Unneeded trigger complexity
