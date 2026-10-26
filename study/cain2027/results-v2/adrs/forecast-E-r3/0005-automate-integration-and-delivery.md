# Automate integration and delivery

* System: Retail demand forecasting

## Context and Problem Statement

A three person team owns the pipeline end to end and wants new ideas to reach production quickly. The design space includes CI/CD pipelines and manually run build and deployment scripts (d:8).

## Decision Drivers

* Production speed
* Protect weekly run

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Production speed decides the choice: automate integration and delivery, accepting the need for release checks to protect the weekly run. This is grounded in the design space alternatives (d:8), but was not included in the checked design points.

### Consequences

* Maintain automated integration and delivery workflows.
* Gate production releases on the selected model quality checks.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Production speed: automates delivery on changes
* Bad, because Protect weekly run: requires safe release checks
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Protect weekly run: deployment can be explicitly initiated
* Bad, because Production speed: manual release workflow
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Good, because Protect weekly run: avoids automatic releases
* Bad, because Production speed: releases remain manual
* Sources: `d:8`, `v:8.4`
