# Orchestrate the weekly ML workflow as a repeatable pipeline

* System: Retail demand forecasting

## Context and Problem Statement

The weekly forecast requires recurring preparation, training, evaluation, and delivery, while new model ideas should move through a consistent path.

## Decision Drivers

* Weekly run
* Fast iteration
* Small team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Repeatable stages reduce manual coordination for a three-person team and provide a controlled path from experimentation to evaluation. The point check attested this combination in MLOps: Model management, deployment, and monitoring with Azure Machine Learning; it also flagged that data ingestion needs a decision.

### Consequences

* Define and maintain pipeline stages.
* Decide the data ingestion approach before finalizing the workflow.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Automates recurring work
* Bad, because Requires pipeline setup
* Sources: `s02_p09`, `s04_p07`, `s04_p15`, `s04_p17`, `s04_p18`, `s06_p07`, `s06_p13`, `s06_p15`, `s08_p01`, `s08_p02`, `s09_p07`, `s09_p08`, `s10_p07`, `s17_p05`, `s17_p06`, `s19_p05`, `s19_p09`, `s20_p05`, `s20_p10`, `s21_p10`, `s25_p01`, `s25_p02`, `s25_p09`, `s28_p03`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible for experiments
* Bad, because Manual handoffs
* Bad, because Harder to repeat weekly
* Sources: `s02_p09`, `s06_p07`
