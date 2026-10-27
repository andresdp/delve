# CI/CD pipeline

*How should integration and delivery be automated?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a fast path to production, but changes must not break the weekly run.

## Decision Drivers

* Fast delivery
* Protect weekly run

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline supports quick, repeatable delivery of model changes, with checks before production release (d:8, v:8.1).

### Consequences

* Delivery automation becomes part of the production path.
* Pipeline failures can delay releases.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates delivery steps
* Good, because Supports frequent changes
* Bad, because Requires pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Simple automation
* Bad, because More manual coordination
* Sources: `d:8`, `v:8.2`
