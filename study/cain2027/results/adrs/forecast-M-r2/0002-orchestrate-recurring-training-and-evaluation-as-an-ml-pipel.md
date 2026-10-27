# Orchestrate recurring training and evaluation as an ML pipeline

* System: Retail demand forecasting

## Context and Problem Statement

The weekly forecast run needs repeatable execution, and model ideas should move through training and evaluation quickly.

## Decision Drivers

* Weekly repeatability
* Fast iteration
* Three-person team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

A connected pipeline makes the weekly workflow repeatable while giving the small team a consistent path to test new model ideas. Practitioner sources describe orchestration for linked preparation, training, evaluation, and deployment stages.

### Consequences

* Define and maintain pipeline stages.
* Decide upstream data ingestion before finalizing the workflow.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable connected stages
* Good, because Automates training and evaluation
* Bad, because Requires orchestration setup
* Sources: `s02_p09`, `s04_p07`, `s06_p07`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible for infrequent changes
* Bad, because Manual run coordination
* Bad, because Harder to repeat reliably
* Sources: `s04_p02`, `s20_p12`
