# Run forecasts as a weekly batch

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts are produced at weekly grain, and the brief names a weekly run rather than an interactive prediction service. A batch workflow fits that cadence and keeps the operational model small.

## Decision Drivers

* Weekly run reliability
* Operational simplicity

## Considered Options

* Weekly batch pipeline
* Continuous online service

## Decision Outcome

Chosen option: "Weekly batch pipeline".

Weekly run reliability and operational simplicity favor scheduled batch processing; this gives up immediate, between-run forecast updates.

### Consequences

* Forecasts refresh on the weekly schedule.
* The pipeline needs a schedule and run status tracking.

## Pros and Cons of the Options

### Weekly batch pipeline

* Good, because Weekly run reliability: bounded scheduled workload
* Good, because Operational simplicity: one execution path
* Bad, because Fast model iteration: changes wait for a run

### Continuous online service

* Good, because Fast model iteration: deploy anytime
* Bad, because Operational simplicity: service upkeep
* Bad, because Weekly run reliability: extra dependencies
