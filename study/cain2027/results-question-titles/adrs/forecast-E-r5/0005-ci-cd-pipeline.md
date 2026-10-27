# CI/CD pipeline

*How should changes reach production safely?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly run. Automated delivery and model quality checks support frequent changes with a validation gate.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Small team

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline enables frequent delivery, with trained-model quality tests as a production gate. The checked design point has no warnings, but is unattested; a rival omitting automation and testing is also unattested and poorly aligned with the brief.

### Consequences

* Gate model releases on quality checks.
* Keep the current weekly run available during rollout.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates delivery
* Good, because Supports frequent changes
* Bad, because Needs pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Automates repeatable steps
* Bad, because Deployment remains manual
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Good, because No automation setup
* Bad, because Slower manual delivery
* Sources: `d:8`, `v:8.4`
