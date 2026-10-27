# Use an orchestrated pipeline for weekly training and evaluation

* System: On-device visual inspection

## Context and Problem Statement

Weekly model updates need repeatable preparation, training, and validation steps for a small team.

## Decision Drivers

* Weekly retraining
* Small team
* Repeatability

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

A recurring weekly cycle benefits from repeatable training and evaluation stages. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” support pipeline coordination.

### Consequences

* The team must maintain pipeline definitions and execution.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Supports evaluation
* Bad, because Pipeline setup effort
* Sources: `s02_p09`, `s06_p07`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Low tooling needs
* Bad, because Manual handoffs
* Bad, because Error-prone repetition
* Sources: `s04_p02`, `s09_p08`
