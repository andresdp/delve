# Coordinate recurring model runs

* System: Retail demand forecasting

## Context and Problem Statement

The system has a weekly run and new model ideas should reach production quickly without disrupting it. The design space presents an orchestrated pipeline as a repeatable alternative to manual script execution.

## Decision Drivers

* Weekly run stability
* Fast model iteration

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Weekly run stability decides the choice: an orchestrated pipeline makes stages repeatable, while manual execution leaves the weekly process dependent on operator actions. Sources including “Architecting a Machine Learning Pipeline” and “MLOps Principles” support pipeline coordination.

### Consequences

* Represent preparation, training, and evaluation as ordered stages.
* Pipeline changes require maintenance and validation.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Weekly run stability: connects repeatable workflow stages
* Bad, because Fast model iteration: requires pipeline setup and upkeep
* Sources: `s02_p09`, `s04_p07`, `s04_p15`, `s04_p17`, `s04_p18`, `s21_p10`, `s25_p01`, `s25_p02`, `s25_p09`, `s28_p03`

### Manual script-driven workflow

* Good, because Fast model iteration: permits direct manual experimentation
* Bad, because Weekly run stability: depends on manual execution across stages
