# Use a CI/CD pipeline for model delivery

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without disrupting the weekly run. The design space compares CI/CD, scripts, an ML orchestrator, and no delivery automation.

## Decision Drivers

* Fast model delivery
* Protect weekly run
* Three person team

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* Machine learning orchestrator (`v:8.3`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline automates repeatable delivery and supports fast iteration. The checked design point had no warnings; no sources attested to the combination.

### Consequences

* Encode build and release steps in the pipeline.
* Keep production promotion behind quality checks.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates repeatable delivery
* Good, because Speeds changes
* Bad, because Requires pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple starting point
* Bad, because Manual release steps
* Sources: `d:8`, `v:8.2`

### Machine learning orchestrator

* Good, because Coordinates multiple pipelines
* Bad, because Additional operating burden
* Sources: `d:8`, `v:8.3`

### No integration or delivery automation

* Good, because No automation setup
* Bad, because Slower, less repeatable releases
* Sources: `d:8`, `v:8.4`
