# How should ML workflow steps be coordinated?

* System: Large-scale document classification

## Context and Problem Statement

At this scale, the workflow needs repeatable preparation, evaluation, and deployment steps to support operational consistency.

## Decision Drivers

* Millions of documents daily
* Production classification

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Choose an orchestrated pipeline for repeatable production workflow stages. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “MLOps: Continuous delivery and automation pipelines in machine learning” support orchestration; the point check includes streaming ingestion as its prerequisite but remains unattested overall.

### Consequences

* Coordinate pipeline triggers with ingestion.
* Version workflow stages and deployment artifacts.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable connected stages
* Good, because Supports automated evaluation and deployment
* Bad, because Requires pipeline operations
* Bad, because Workflow depends on ingestion design
* Sources: `s02_p09`, `s04_p15`, `s06_p07`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Flexible for occasional runs
* Bad, because Manual transitions add toil
* Bad, because Harder to repeat consistently
* Sources: `s04_p02`, `s20_p12`
