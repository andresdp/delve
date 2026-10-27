# Use a CI/CD pipeline for model and system releases

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly, while weekly runs must remain stable. Automated integration and delivery provides a repeatable release path (d:8).

## Decision Drivers

* Fast model releases
* Protect weekly run

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* Machine learning orchestrator (`v:8.3`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

CI/CD automates the release path and supports rapid model updates with repeatable checks (d:8, v:8.1). The checked design point had no warnings, but its combination was unattested; a rival with manual deployment scripts and no automation was also unattested.

### Consequences

* Maintain automated build and release definitions.
* Keep weekly forecasting runs independent of code commits.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates repeatable releases
* Good, because Shortens delivery cycle
* Bad, because Needs pipeline upkeep
* Bad, because Requires release checks
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple automation
* Good, because Manual release control
* Bad, because More operator effort
* Bad, because Less consistent release process
* Sources: `d:8`, `v:8.2`

### Machine learning orchestrator

* Good, because Coordinates multiple pipelines
* Good, because Supports complex workflows
* Bad, because Adds platform overhead
* Bad, because May exceed team needs
* Sources: `d:8`, `v:8.3`
