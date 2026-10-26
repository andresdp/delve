# How to deploy and recover model versions?

* System: Retail demand forecasting

## Context and Problem Statement

A model change should reach production quickly while allowing recovery if it threatens the weekly run. The design space includes rollback and multiple or single production versions (d:10).

## Decision Drivers

* Protect weekly run
* Ship model ideas quickly

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Protecting the weekly run decides the choice: retain a previous deployable model for recovery, at the cost of managing versioned artifacts (d:10, v:10.2).

### Consequences

* Keep the previous model available for redeployment.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Protect weekly run: restore prior model
* Bad, because Small team: preserve and manage deployable versions
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Ship model ideas quickly: run versions side by side
* Bad, because Small team: more production complexity

### Single model in production

* Good, because Small team: simple production state
* Bad, because Protect weekly run: no explicit recovery path
