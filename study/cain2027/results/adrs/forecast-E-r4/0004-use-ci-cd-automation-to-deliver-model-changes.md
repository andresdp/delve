# Use CI/CD automation to deliver model changes

* System: Retail demand forecasting

## Context and Problem Statement

The team wants new model ideas to reach production quickly without disrupting the weekly run. The design space compares CI/CD pipelines, scripts, orchestration, and no automation (d:8).

## Decision Drivers

* Fast model iteration
* Protect weekly run

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* Machine learning orchestrator (`v:8.3`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline supports automated delivery and faster iteration; the design point with this choice and batch processing was novel and unattested, with no warnings (d:8, v:8.1; d:15, v:15.1).

### Consequences

* Automate build and delivery steps.
* Maintain delivery checks as the pipeline evolves.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates delivery
* Bad, because Requires pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple automation
* Bad, because Delivery remains manual
* Sources: `d:8`, `v:8.2`

### Machine learning orchestrator

* Good, because Coordinates multiple pipelines
* Bad, because Adds orchestration overhead
* Sources: `d:8`, `v:8.3`

### No integration or delivery automation

* Good, because No automation setup
* Bad, because Slows production changes
* Sources: `d:8`, `v:8.4`
