# Orchestrated ML pipeline

*How should weekly ML work be coordinated?*

* System: Retail demand forecasting

## Context and Problem Statement

The weekly run must be repeatable, while new model ideas should reach production quickly. A three-person team needs a workflow that limits manual coordination.

## Decision Drivers

* weekly reliability
* fast experimentation
* small team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

The chosen workflow supports a safe weekly run and fast iterations. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Productionizing Machine Learning with a Microservices Architecture” describe repeatable stages; the design point supports this direction, though it warns that data ingestion must be decided first.

### Consequences

* Pipeline stages and dependencies need ownership.
* Changes require pipeline validation.
* Data ingestion design remains to be settled.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because repeatable stages
* Good, because automated handoffs
* Bad, because setup effort
* Bad, because pipeline maintenance
* Sources: `s02_p09`, `s04_p07`, `s06_p07`

### Manual script-driven workflow

* Good, because low initial overhead
* Good, because direct control
* Bad, because manual coordination
* Bad, because harder repeatability
* Sources: `s04_p02`, `s09_p08`, `s20_p12`
