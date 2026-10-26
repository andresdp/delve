# How should weekly integration and delivery be automated?

* System: On-device visual inspection

## Context and Problem Statement

A small team needs a repeatable way to package and push weekly model updates. Automation reduces manual work but takes initial setup.

## Decision Drivers

* Weekly retraining
* Small team
* Reproducibility

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

The small-team driver decides for automated delivery, trading setup and upkeep for repeatable weekly packaging and deployment.

### Consequences

* The pipeline needs checks before device rollout.
* Offline devices require a staged transfer mechanism.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Small team: automates repeatable delivery
* Bad, because Budget: requires pipeline setup and upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Budget: lightweight automation
* Bad, because Small team: more manual release coordination
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Good, because Budget: no pipeline infrastructure
* Bad, because Weekly retraining: manual deployments add effort
* Sources: `d:8`, `v:8.4`
