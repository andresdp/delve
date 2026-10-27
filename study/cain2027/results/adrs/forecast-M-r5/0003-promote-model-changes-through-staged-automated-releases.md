# Promote model changes through staged automated releases

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly, while releases must not disrupt the weekly forecast run. Staged validation and promotion provide a controlled path from code change to production.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Automated delivery

## Considered Options

* Unified release automation (`v:19.1`)
* Commit-triggered staged release automation (`v:19.2`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

The checked point includes this accepted option. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” describe automated staged delivery, which suits rapid iteration while providing checkpoints before production.

### Consequences

* Production promotion depends on passing configured checks.
* The team must maintain release stages and gates.

## Pros and Cons of the Options

### Unified release automation

* Good, because One release process
* Good, because Automates build and packaging
* Bad, because Limited stage-specific gates
* Bad, because Rollback not explicit

### Commit-triggered staged release automation

* Good, because Changes trigger delivery
* Good, because Supports staged validation
* Bad, because Needs release pipeline
* Bad, because Gate configuration required
* Sources: `s06_p02`, `s06_p13`, `s08_p01`
