# How should model updates be deployed?

* System: Card-fraud scoring service

## Context and Problem Statement

Model releases must be traceable and recoverable without disrupting transaction scoring. The design space includes a previous-version rollback option and a multi-version production option.

## Decision Drivers

* model-version traceability
* scoring availability
* safe updates

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

A previous version provides a direct recovery option while retaining a clear deployed version for audit; it does not by itself specify the rollout procedure. (d:10, v:10.2)

### Consequences

* Retain deployable prior model artifacts.
* Log active model version with each score.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because recovery path
* Good, because version changes explicit
* Bad, because rollback takes deployment action
* Bad, because requires prior artifact retention
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because multiple versions available
* Good, because supports staged rollout
* Bad, because routing complexity
* Bad, because more serving capacity
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because simple active version
* Good, because lower serving complexity
* Bad, because no concurrent version option
* Bad, because switch may disrupt service
* Sources: `d:10`, `v:10.3`
