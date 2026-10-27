# Use an orchestrated ML pipeline for repeatable model operations

* System: Large-scale document classification

## Context and Problem Statement

A high-volume classification service needs coordinated model workflows, while operators need visibility into changing quality. The brief does not specify a retraining cadence.

## Decision Drivers

* High daily volume
* Quality drift visibility

## Considered Options

* Manual script-driven workflow (`v:32.1`)
* Orchestrated ML pipeline (`v:32.2`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

An orchestrated pipeline supports repeatable preparation, evaluation, and deployment as volume and model quality change. It also provides a basis for later drift-triggered workflows; no source attested to the complete checked design point.

### Consequences

* Automate and observe workflow stages.
* Define promotion and retraining controls.

## Pros and Cons of the Options

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Human-controlled steps
* Bad, because Manual transitions
* Bad, because Poor fit for frequent operations
* Sources: `s04_p02`

### Orchestrated ML pipeline

* Good, because Repeatable stages
* Good, because Coordinates evaluation and deployment
* Bad, because Requires pipeline operations
* Sources: `s02_p09`, `s04_p07`
