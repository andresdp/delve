# CI/CD pipeline

*How should model delivery be automated?*

* System: On-device visual inspection

## Context and Problem Statement

A small team needs to distribute retrained models to devices on a regular basis. The delivery path should automate repeatable build and deployment work.

## Decision Drivers

* Weekly model rollout
* Small team
* Tight budget

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline reduces repeated manual steps in weekly model delivery, which suits the small team (d:8, v:8.1).

### Consequences

* The pipeline must package and distribute device-compatible models.
* Pipeline failures can delay rollout.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Repeatable delivery
* Good, because Less manual work
* Bad, because Pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple starting point
* Bad, because Manual execution
* Bad, because More operator effort
* Sources: `d:8`, `v:8.2`
