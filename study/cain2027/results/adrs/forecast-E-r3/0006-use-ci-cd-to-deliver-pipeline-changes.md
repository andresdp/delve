# Use CI/CD to deliver pipeline changes

* System: Retail demand forecasting

## Context and Problem Statement

The team wants model ideas to reach production quickly while protecting the weekly run. The design space distinguishes CI/CD from deployment scripts and no delivery automation (d:8), and identifies pipeline components as deployable artifacts (d:25).

## Decision Drivers

* Fast delivery
* Weekly run stability
* Three-person team

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Use CI/CD to build, test, and deploy the ML pipelines and components needed for pipeline runs (d:8, v:8.1; d:25, v:25.2). The checked design point produced no warnings, but no attesting sources; the combination is novel in this workspace.

### Consequences

* Automate checks before delivery.
* Keep production promotion controlled to protect the weekly run.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates delivery
* Good, because Supports frequent changes
* Bad, because Requires pipeline maintenance
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple automation
* Bad, because More manual coordination
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Good, because No automation setup
* Bad, because Slower, error-prone releases
* Sources: `d:8`, `v:8.4`
