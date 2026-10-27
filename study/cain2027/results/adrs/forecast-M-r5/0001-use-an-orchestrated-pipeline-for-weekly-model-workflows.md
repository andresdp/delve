# Use an orchestrated pipeline for weekly model workflows

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasts must run reliably, and the three-person team owns the full pipeline. Repeatable stages support scheduled execution and delivery of model changes.

## Decision Drivers

* Reliable weekly run
* Small team
* Fast iteration

## Considered Options

* Manual script-driven workflow (`v:32.1`)
* Orchestrated ML pipeline (`v:32.2`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

The checked design point includes this accepted value, though it is unattested as a combination and warns that data ingestion must also be decided. Sources such as “MLOps: Continuous delivery and automation pipelines in machine learning” describe repeatable pipeline stages; this fits the weekly run and the team’s need to move ideas into production.

### Consequences

* Pipeline changes need review and maintenance.
* Data ingestion remains an open decision.

## Pros and Cons of the Options

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible for experiments
* Bad, because Manual handoffs
* Bad, because Harder to repeat reliably

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Automates handoffs
* Bad, because Needs orchestration setup
* Bad, because Pipeline maintenance
* Sources: `s02_p09`, `s06_p07`, `s06_p13`
