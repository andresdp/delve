# CI/CD pipeline with rollback to previous model version

*How should changes reach production safely?*

* System: Retail demand forecasting

## Context and Problem Statement

The team wants new model ideas in production quickly without disrupting the weekly run, so automated delivery and rollback matter (d:8, d:10).

## Decision Drivers

* Fast iteration
* Weekly run reliability
* Small team

## Considered Options

* CI/CD pipeline with rollback to previous model version (`v:8.1 / v:10.2`)
* Build and Deployment scripts with single model in production (`v:8.2 / v:10.3`)
* CI/CD pipeline with N versions in production (`v:8.1 / v:10.1`)

## Decision Outcome

Chosen option: "CI/CD pipeline with rollback to previous model version" (`v:8.1 / v:10.2`).

Weekly run reliability decides the choice: automate delivery while retaining a known recovery path, accepting the effort to establish and maintain CI/CD and rollback procedures.

### Consequences

* Make model promotion and rollback repeatable pipeline steps.
* Keep the prior production model available for recovery.

## Pros and Cons of the Options

### CI/CD pipeline with rollback to previous model version

* Good, because Fast iteration: automates delivery
* Good, because Weekly run reliability: supports restoring a prior model
* Bad, because Small team: requires pipeline and rollback procedures
* Sources: `d:8`, `v:8.1`, `d:10`, `v:10.2`

### Build and Deployment scripts with single model in production

* Good, because Small team: few deployment components
* Bad, because Fast iteration: manual execution slows changes
* Bad, because Weekly run reliability: recovery is less explicit
* Sources: `d:8`, `v:8.2`, `d:10`, `v:10.3`

### CI/CD pipeline with N versions in production

* Good, because Fast iteration: supports parallel model versions
* Bad, because Small team: multiple production versions add operating work
* Sources: `d:8`, `v:8.1`, `d:10`, `v:10.1`
