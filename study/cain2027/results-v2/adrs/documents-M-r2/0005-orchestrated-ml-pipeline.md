# Orchestrated ML pipeline

*How should ML workflow stages be coordinated?*

* System: Large-scale document classification

## Context and Problem Statement

At this volume, repeated classification runs need dependable preparation, scoring, and evaluation stages. Teams also need a consistent workflow to operate and evolve the system.

## Decision Drivers

* High daily volume
* Repeatable operation
* Multiple teams

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Repeatable operation decides the choice: an orchestrated pipeline connects recurring stages, as described in “Architecting a Machine Learning Pipeline” and “MLOps: Continuous delivery and automation pipelines in machine learning.” This costs more to establish than manual scripts, but supports frequent, consistent runs.

### Consequences

* Pipeline stages need operational ownership.
* Failures require retry and alert policies.
* The ingestion mechanism must be decided first.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable operation: connects workflow stages
* Good, because High volume: automates recurring runs
* Bad, because Cost: requires pipeline setup and maintenance
* Sources: `s02_p09`, `s04_p07`, `s06_p07`

### Manual script-driven workflow

* Good, because Cost: simple to start
* Bad, because High volume: manual transitions limit repeatability
* Sources: `s04_p02`, `s20_p12`, `s21_p07`
