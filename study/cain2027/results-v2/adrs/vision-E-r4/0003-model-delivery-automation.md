# Model delivery automation

* System: On-device visual inspection

## Context and Problem Statement

A small team must push weekly model updates to cameras without relying on continuous network access at the devices.

## Decision Drivers

* Small team
* Weekly releases
* Tight budget

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Small team capacity decides the choice: automate the recurring weekly build and release workflow. The trade-off is time spent establishing and maintaining the pipeline.

### Consequences

* Include model validation and packaging in delivery automation.
* Stage artifacts for devices to retrieve when connectivity returns.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Small team: automates repeatable delivery
* Bad, because Tight budget: pipeline setup and maintenance
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Tight budget: lightweight tooling
* Bad, because Small team: manual release work
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Bad, because Weekly releases: repetitive manual work
* Bad, because Small team: error-prone release process
* Sources: `d:8`, `v:8.4`
