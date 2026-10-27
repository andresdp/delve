# Workflow execution coordination

* System: Retail demand forecasting

## Context and Problem Statement

Weekly preparation, training, evaluation, and scoring must repeat reliably, while model ideas should move through the same controlled path. Manual execution would leave recurring steps dependent on team members.

## Decision Drivers

* Reliable weekly run
* Fast experimentation
* Three-person team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

An orchestrated pipeline makes the recurring weekly run repeatable and gives new candidates a consistent route through evaluation. Sources “Architecting a Machine Learning Pipeline” and “MLOps: Continuous delivery and automation pipelines in machine learning” support this approach; the checked point has no warnings, though the combination is unattested.

### Consequences

* Pipeline definitions need version control.
* Failed stages require clear retry and recovery behavior.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Supports evaluation gates
* Bad, because Pipeline upkeep
* Bad, because Initial setup effort
* Sources: `s02_p09`, `s04_p07`, `s06_p07`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible exploration
* Bad, because Manual coordination
* Bad, because Harder to reproduce
