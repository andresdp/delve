# How should weekly runs be coordinated?

* System: Retail demand forecasting

## Context and Problem Statement

The system runs a recurring forecast per store and product, and new model ideas should reach production quickly. Repeatable stages can make the weekly run easier to operate consistently.

## Decision Drivers

* Weekly reliability
* Fast iteration
* Small team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

A pipeline supports recurring preparation, training, evaluation, and deployment while helping a small team move changes through a repeatable process. The design point and its rival were both novel and flagged that data ingestion also needs a decision; Architecting a Machine Learning Pipeline and Google’s MLOps guidance support orchestration.

### Consequences

* Pipeline stages and dependencies need maintenance.
* Data ingestion must be decided alongside coordination.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Connects evaluation to deployment
* Bad, because Requires pipeline setup
* Sources: `s02_p09`, `s04_p07`, `s06_p07`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible for experiments
* Bad, because Manual handoffs
* Bad, because Harder to repeat weekly
* Sources: `s04_p02`, `s09_p08`, `s20_p12`
