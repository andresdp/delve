# Use an orchestrated ML pipeline

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasting needs repeatable preparation, training, evaluation, and release steps. A three-person team benefits from reducing manual coordination.

## Decision Drivers

* Weekly run reliability
* Small team
* Fast iteration

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Choose a repeatable pipeline to support the weekly run and get model changes through preparation, evaluation, and deployment with less manual coordination. Practitioners describe connected pipeline stages in “MLOps: Continuous delivery and automation pipelines in machine learning.”

### Consequences

* Pipeline stages and dependencies need maintenance.
* Workflow orchestration becomes a production dependency.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Automates handoffs
* Bad, because Pipeline upkeep
* Sources: `s02_p09`, `s06_p07`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible execution
* Bad, because Manual coordination
* Bad, because Harder to repeat
* Sources: `s04_p02`, `s20_p12`
