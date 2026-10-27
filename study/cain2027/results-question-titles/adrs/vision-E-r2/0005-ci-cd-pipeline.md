# CI/CD pipeline

*How is model delivery automated?*

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must reach devices in production. The design space considers CI/CD, scripts, and an ML orchestrator (d:8).

## Decision Drivers

* Weekly model delivery
* Tight infrastructure budget
* Small team

## Considered Options

* Build and Deployment scripts (`v:8.2`)
* CI/CD pipeline (`v:8.1`)
* Machine learning orchestrator (`v:8.3`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline makes weekly model delivery repeatable and can automate checks before promoting packages to devices (d:8, v:8.1). The checked combination had no warnings; the rival combination also had no warnings, and neither was attested by sources.

### Consequences

* The pipeline must package models for device installation.
* Pipeline maintenance adds ongoing work.

## Pros and Cons of the Options

### Build and Deployment scripts

* Good, because Low infrastructure overhead
* Good, because Straightforward deployment steps
* Bad, because More manual coordination
* Bad, because Limited workflow visibility
* Sources: `d:8`, `v:8.2`

### CI/CD pipeline

* Good, because Repeatable delivery
* Good, because Automated checks and deployment
* Bad, because Pipeline setup and maintenance
* Bad, because Device fleet integration needed
* Sources: `d:8`, `v:8.1`

### Machine learning orchestrator

* Good, because Coordinates multiple ML workflows
* Good, because Central workflow management
* Bad, because Added platform overhead
* Bad, because May exceed team needs
* Sources: `d:8`, `v:8.3`
