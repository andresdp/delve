# CI/CD pipeline

*How should integration and delivery be automated?*

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must be pushed to production devices each week. The design space compares a CI/CD pipeline with deployment scripts and an ML orchestrator.

## Decision Drivers

* weekly model delivery
* small team
* tight budget

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline can make weekly delivery repeatable for a small team. The checked combination had no warnings, but no attesting sources.

### Consequences

* Automate model packaging and device delivery.
* Maintain the pipeline as deployment needs change.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because repeatable delivery
* Good, because automates routine steps
* Bad, because pipeline setup and upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because simple starting point
* Bad, because manual execution
* Bad, because less integrated checks
* Sources: `d:8`, `v:8.2`
