# Use deployment scripts for weekly model delivery

* System: On-device visual inspection

## Context and Problem Statement

Trained models must be pushed to devices. The team is small and the infrastructure budget is tight.

## Decision Drivers

* Weekly delivery
* Small team
* Tight budget

## Considered Options

* Build and Deployment scripts (`v:8.2`)
* CI/CD pipeline (`v:8.1`)
* Machine learning orchestrator (`v:8.3`)

## Decision Outcome

Chosen option: "Build and Deployment scripts" (`v:8.2`).

Scripts provide automated deployment steps with a comparatively lightweight operating footprint for the stated team and budget (d:8, v:8.2).

### Consequences

* The team maintains the scripts and their execution environment.
* Delivery coordination remains relatively simple.

## Pros and Cons of the Options

### Build and Deployment scripts

* Good, because Automates deployment steps
* Good, because Lightweight approach
* Bad, because Less orchestration support
* Sources: `d:8`, `v:8.2`

### CI/CD pipeline

* Good, because Automates continuous delivery
* Good, because Repeatable workflow
* Bad, because Pipeline infrastructure needed
* Sources: `d:8`, `v:8.1`

### Machine learning orchestrator

* Good, because Orchestrates multiple pipelines
* Bad, because More infrastructure to operate
* Sources: `d:8`, `v:8.3`
