# ML workflow execution coordination

* System: Retail demand forecasting

## Context and Problem Statement

The team needs a repeatable weekly run and a quick path from model idea to production.

## Decision Drivers

* Weekly run reliability
* Fast iteration
* Three-person team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

An orchestrated pipeline makes the weekly preparation, training, evaluation, and deployment sequence repeatable while reducing manual coordination for a small team. Support includes “MLOps: Continuous delivery and automation pipelines in machine learning” and “Productionizing Machine Learning with a Microservices Architecture.”

### Consequences

* Pipeline stages and dependencies need maintenance.
* Model changes can follow the same run path.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Automates handoffs
* Bad, because Pipeline upkeep
* Bad, because Initial setup effort
* Sources: `s06_p07`, `s06_p13`, `s04_p07`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible exploration
* Bad, because Manual handoffs
* Bad, because Harder to repeat
