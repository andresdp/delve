# Automatically build, test, and deploy models and system components

* System: Retail demand forecasting

## Context and Problem Statement

The team needs a quick path for model ideas while preserving the weekly run. The design space distinguishes automating model and system component delivery from automating pipeline components (d:25).

## Decision Drivers

* Fast model releases
* Release safety

## Considered Options

* Build, test, and deploy models to be served and other system components (`v:25.1`)
* Build, test, and deploy machine learning pipelines and components needed during pipeline runs (`v:25.2`)
* No automated deployment (`v:25.3`)

## Decision Outcome

Chosen option: "Build, test, and deploy models to be served and other system components" (`v:25.1`).

Automating model and component release directly serves the goal of getting new model ideas into production quickly (d:25, v:25.1).

### Consequences

* Gate promotion on model and system checks.
* Keep release automation separate from the weekly forecast schedule.

## Pros and Cons of the Options

### Build, test, and deploy models to be served and other system components

* Good, because Automates model releases
* Good, because Covers serving components
* Bad, because Requires release automation
* Bad, because Needs acceptance gates
* Sources: `d:25`, `v:25.1`

### Build, test, and deploy machine learning pipelines and components needed during pipeline runs

* Good, because Automates run components
* Good, because Keeps pipeline code deployable
* Bad, because Does not alone release served models
* Bad, because Adds pipeline maintenance
* Sources: `d:25`, `v:25.2`

### No automated deployment

* Good, because No deployment tooling
* Good, because Manual control
* Bad, because Slower model delivery
* Bad, because More operator error risk
* Sources: `d:25`, `v:25.3`
