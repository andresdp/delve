# How to automate integration and delivery?

* System: Retail demand forecasting

## Context and Problem Statement

A three-person team owns the pipeline end to end, and new model ideas should reach production quickly without breaking the weekly run. The brief does not define a specific deployment process.

## Decision Drivers

* Fast iteration
* Weekly run reliability
* Small team

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* Machine learning orchestrator (`v:8.3`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Fast iteration decides the choice: CI/CD automates repeated integration and delivery work. To protect the weekly run, releases need checks and controlled promotion, which add pipeline setup and maintenance.

### Consequences

* Automate repeatable build and delivery steps.
* Gate model changes before production promotion.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Fast iteration: automate build and delivery
* Bad, because Weekly run reliability: faulty changes can reach production without gates
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Weekly run reliability: team controls deployment timing
* Bad, because Small team: repeated manual release work
* Bad, because Fast iteration: release steps can slow changes
* Sources: `d:8`, `v:8.2`

### Machine learning orchestrator

* Good, because Weekly run reliability: coordinates pipeline components
* Bad, because Small team: added platform and maintenance burden
* Sources: `d:8`, `v:8.3`

### No integration or delivery automation

* Good, because Small team: no automation setup
* Bad, because Fast iteration: manual delivery slows releases
* Bad, because Weekly run reliability: less consistent execution
* Sources: `d:8`, `v:8.4`
