# End-to-end reproducible lifecycle governance

*How much lifecycle state should be versioned?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly training should be reproducible so the team can identify which labelled data and training configuration produced a deployed model. The design space ranges from artifact-only tracking to lifecycle-wide traceability.

## Decision Drivers

* Reproducibility
* Safe weekly updates
* Small team

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Artifact version control (`v:20.1`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Reproducibility decides the choice: link datasets, training runs, artifacts, and deployment status so weekly results can be traced, accepting added metadata work. “MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support lifecycle traceability.

### Consequences

* Record dataset versions and training configuration for each candidate.
* Keep traceability tooling and metadata proportional to the team’s capacity.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Reproducibility: links data, runs, artifacts, and deployment
* Bad, because Small team: broader metadata upkeep
* Sources: `s21_p03`, `s21_p09`, `s25_p02`

### Artifact version control

* Good, because Small team: versions deployable artifacts
* Bad, because Reproducibility: omits training and dataset context

### Pipeline and experiment version control

* Good, because Reproducibility: records pipeline and experiment changes
* Bad, because Safe weekly updates: deployment health is not included
