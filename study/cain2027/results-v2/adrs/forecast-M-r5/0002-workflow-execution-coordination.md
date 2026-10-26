# Workflow execution coordination

* System: Retail demand forecasting

## Context and Problem Statement

A weekly end-to-end run must execute consistently, while a three-person team needs to develop and deliver model ideas without relying on manual handoffs.

## Decision Drivers

* Protect weekly run
* Fast production changes
* Small team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Protecting the weekly run decides: an orchestrated pipeline makes preparation, training, and evaluation repeatable, at the cost of maintaining the workflow. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Architecting a Machine Learning Pipeline” support this direction; the checked point has no warnings but is unattested as a complete combination.

### Consequences

* Pipeline changes need review and maintenance.
* Model experiments can run through the same stages as weekly production.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Weekly run: repeatable connected stages
* Good, because Small team: automates handoffs
* Bad, because Fast production changes: pipeline upkeep
* Sources: `s02_p09`, `s06_p07`

### Manual script-driven workflow

* Good, because Fast production changes: direct edits
* Bad, because Weekly run: manual transitions can vary
* Sources: `s04_p02`, `s20_p12`
