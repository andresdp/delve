# How should retraining and evaluation steps be coordinated?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining and pre-release evaluation require ordered, repeatable workflow steps. Manual execution may reduce initial setup, but adds recurring work for a small team.

## Decision Drivers

* Weekly retraining cadence
* Small team
* Reproducibility

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

The weekly cadence decides the choice: orchestrate preparation, training, evaluation, and deployment so the recurring workflow is repeatable. This gives up the lower initial operational burden of manual scripts. The checked design point—edge inference, weekly schedule trigger, offline evaluation, progressive release, and an orchestrated pipeline—has no attesting source combination; a rival swapping in service inference and drift-triggered retraining also has no attesting sources, so the combination remains an informed design choice rather than an attested one.

### Consequences

* Maintain the pipeline definition alongside model code.
* Allocate time for pipeline setup and operational ownership.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Weekly cadence: connects repeatable workflow stages
* Good, because Reproducibility: standardizes preparation, training, and evaluation
* Bad, because Infrastructure budget: orchestration adds setup and operations
* Bad, because Small team: pipeline changes require maintenance

### Manual script-driven workflow

* Good, because Infrastructure budget: avoids orchestration infrastructure
* Good, because Small team: simple when workflows are infrequent
* Bad, because Weekly cadence: recurring manual steps consume team time
* Bad, because Reproducibility: execution depends on consistent operator practice
