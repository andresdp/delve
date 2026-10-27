# Automate model delivery with a CI/CD pipeline

* System: On-device visual inspection

## Context and Problem Statement

A retrained model must reach production devices every week. Automating delivery reduces repeated manual work for the small team.

## Decision Drivers

* weekly model updates
* small team
* tight budget

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A repeatable pipeline suits the weekly release cadence and can reduce the effort of delivering updates across devices.

### Consequences

* Maintain pipeline configuration and credentials.
* Define checks before deployment to devices.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because repeatable deployments
* Good, because less manual effort
* Bad, because pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because simple automation
* Good, because limited infrastructure
* Bad, because manual execution
* Bad, because operator dependent
* Sources: `d:8`, `v:8.2`
