# Use a CI/CD pipeline for weekly model delivery

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly and must reach production devices with limited team capacity.

## Decision Drivers

* Weekly updates
* Small team
* Tight budget

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Automated delivery fits the weekly release cadence and reduces operational work for a small team (d:8, v:8.1).

### Consequences

* Maintain deployment automation.
* Validate artifacts before release.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Repeatable delivery
* Good, because Automates routine work
* Bad, because Pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple automation
* Good, because Low setup
* Bad, because Manual operation
* Bad, because Error-prone repetition
* Sources: `d:8`, `v:8.2`
