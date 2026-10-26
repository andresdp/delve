# CI/CD pipeline

*How to automate integration and delivery?*

* System: Retail demand forecasting

## Context and Problem Statement

A three-person team needs to move model ideas into production without relying on manual deployment steps. The design space compares CI/CD, deployment scripts, and an ML orchestrator (d:8).

## Decision Drivers

* Ship model ideas quickly
* Protect weekly run
* Small team

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* Machine learning orchestrator (`v:8.3`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Shipping ideas quickly decides the choice: automate integration and delivery, accepting the ongoing effort of maintaining the pipeline (d:8, v:8.1).

### Consequences

* Require checks to pass before delivery.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Ship model ideas quickly: automates delivery
* Bad, because Small team: pipeline setup and maintenance
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Small team: simpler automation
* Bad, because Ship model ideas quickly: manual deployment remains

### Machine learning orchestrator

* Good, because Protect weekly run: coordinates multiple pipelines
* Bad, because Small team: added platform complexity
