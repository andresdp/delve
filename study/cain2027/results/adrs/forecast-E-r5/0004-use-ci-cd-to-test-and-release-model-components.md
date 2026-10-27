# Use CI/CD to test and release model components

* System: Retail demand forecasting

## Context and Problem Statement

A three-person team owns the pipeline, and new model ideas should reach production quickly without breaking the weekly run. The design space covers CI/CD automation and what it builds and deploys (d:8, d:25).

## Decision Drivers

* Small team
* Fast model iteration
* Protect weekly run

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)
* Build, test, and deploy models to be served and other system components (`v:25.1`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

CI/CD supports frequent, repeatable releases for a small team; configure it to build and test served models and related components (d:25, v:25.1). Testing trained model quality is also a relevant pipeline test (d:26, v:26.9). The selected combination was checked with no warnings, but the design point is unattested.

### Consequences

* Automate quality checks before promotion.
* Keep release configuration and pipeline definitions maintained.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates integration and delivery
* Good, because Supports repeatable releases
* Bad, because Requires pipeline maintenance
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple to start
* Bad, because Manual release coordination
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Good, because No automation setup
* Bad, because Slows safe iteration
* Sources: `d:8`, `v:8.4`

### Build, test, and deploy models to be served and other system components

* Good, because Automates model and component checks
* Good, because Supports consistent releases
* Bad, because Needs deployment configuration
* Sources: `d:25`, `v:25.1`
