# CI/CD pipeline

*How should changes reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

The team wants model ideas to reach production quickly without breaking the weekly forecast run.

## Decision Drivers

* Fast delivery
* Three-person team
* Protect weekly run

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

CI/CD supports rapid, repeatable delivery; pair it with automated checks and a protected weekly schedule. The checked combination had no warnings and no attested sources.

### Consequences

* Changes require a maintained delivery pipeline.
* Release checks become part of the path to production.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates delivery steps
* Good, because Shortens release path
* Bad, because Requires pipeline maintenance
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Automates repeatable commands
* Bad, because Manual release coordination
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Bad, because Slower, error-prone delivery
* Sources: `d:8`, `v:8.4`
