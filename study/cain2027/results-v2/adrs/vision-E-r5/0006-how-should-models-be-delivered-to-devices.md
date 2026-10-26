# How should models be delivered to devices?

* System: On-device visual inspection

## Context and Problem Statement

A small team must push weekly model updates to production devices.

## Decision Drivers

* Weekly updates
* Tight budget
* Reproducibility

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Weekly updates decide the choice: a pipeline reduces repeated delivery work for the small team. This gives up the lower initial setup cost of scripts. The design space has no source passages; this choice is grounded in d:8 and v:8.1.

### Consequences

* Deployment steps are automated.
* Pipeline maintenance is required.
* Device connectivity and update windows need coordination.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Weekly updates: automates recurring delivery
* Good, because Reproducibility: standardizes deployment steps
* Bad, because Tight budget: requires pipeline setup and upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Tight budget: small initial setup
* Bad, because Weekly updates: manual execution adds effort
* Bad, because Reproducibility: steps can drift
* Sources: `d:8`, `v:8.2`
