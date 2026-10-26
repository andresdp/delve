# Version pipelines and experiments together

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a forecast requires more than retaining its data: the pipeline and experiment configuration must also be recoverable. The design space distinguishes this from versioning artifacts alone.

## Decision Drivers

* Past-week reproducibility
* Fast model iteration

## Considered Options

* Pipeline and experiment version control (`v:20.2`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Pipeline and experiment version control" (`v:20.2`).

Past-week reproducibility decides the choice because artifact versions alone do not capture how a forecast was produced. “Productionizing Machine Learning with a Microservices Architecture” and “AutoML” support versioning pipelines and experiments together.

### Consequences

* Record pipeline and experiment versions with each run.
* The team maintains more lifecycle metadata.

## Pros and Cons of the Options

### Pipeline and experiment version control

* Good, because Reproducibility: compares and recovers configurations and runs
* Bad, because Fast model iteration: adds versioning and tracking work
* Sources: `s04_p01`, `s04_p03`, `s04_p05`, `s04_p15`, `s04_p18`, `s17_p03`

### Artifact version control

* Good, because Reproducibility: preserves model artifacts and dependencies
* Bad, because Past-week reproducibility: omits pipeline and experiment history
