# Retraining execution

* System: On-device visual inspection

## Context and Problem Statement

Weekly training should use new labels with limited infrastructure and a small team. The brief gives no indication that training needs to exceed one machine.

## Decision Drivers

* Low infrastructure cost
* Weekly retraining
* Small-team operations

## Considered Options

* Automated retraining pipeline (`v:6.5`)
* Manual retraining trigger (`v:6.14`)

## Decision Outcome

Chosen option: "Automated retraining pipeline" (`v:6.5`).

Weekly retraining decides the choice: automation makes the recurring update repeatable, while adding pipeline maintenance. “MLOps Principles” and “MLOps: Continuous delivery and automation pipelines in machine learning” describe automated retraining workflows.

### Consequences

* Training and release failures need visible status.
* The system needs an operator path for investigating failed runs.

## Pros and Cons of the Options

### Automated retraining pipeline

* Good, because Weekly retraining: automates recurring model updates
* Bad, because Small-team operations: pipeline needs maintenance
* Sources: `s06_p07`, `s22_p03`

### Manual retraining trigger

* Good, because Low infrastructure cost: avoids orchestration
* Bad, because Weekly retraining: manual recurring work
