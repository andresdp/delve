# Orchestrated ML pipeline

*How should weekly training and validation run?*

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly, which makes repeatable sequencing of training, evaluation, and release valuable to a small team. The design space contrasts manual script execution with an orchestrated pipeline.

## Decision Drivers

* Weekly cadence
* Small team
* Repeatability

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

The weekly cadence decides the choice: a repeatable pipeline reduces recurring manual work, though it adds workflow upkeep. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” support pipeline-based execution.

### Consequences

* Define and maintain training, evaluation, and release stages.
* Keep pipeline dependencies manageable for the small team.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Weekly cadence: repeatable connected stages
* Bad, because Small team: pipeline upkeep
* Sources: `s06_p07`, `s22_p08`

### Manual script-driven workflow

* Good, because Small team: few orchestration components
* Bad, because Weekly cadence: repeated manual execution
* Sources: `s02_p08`
