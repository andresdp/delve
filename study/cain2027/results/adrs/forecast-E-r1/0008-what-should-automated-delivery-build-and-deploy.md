# What should automated delivery build and deploy?

* System: Retail demand forecasting

## Context and Problem Statement

The system depends on both model artifacts and the components that run the forecasting workflow.

## Decision Drivers

* Safe model changes
* Reliable pipeline

## Considered Options

* Build, test, and deploy models to be served and other system components (`v:25.1`)
* No automated deployment (`v:25.3`)

## Decision Outcome

Chosen option: "Build, test, and deploy models to be served and other system components" (`v:25.1`).

Automating build, test, and deployment for models and system components supports rapid releases while protecting the weekly workflow (d:25, v:25.1).

### Consequences

* Model and component releases use automated checks.
* Deployment automation must cover the weekly run’s dependencies.

## Pros and Cons of the Options

### Build, test, and deploy models to be served and other system components

* Good, because Covers production components
* Good, because Automates model delivery
* Bad, because Broader release scope
* Sources: `d:25`, `v:25.1`

### No automated deployment

* Good, because No deployment pipeline upkeep
* Bad, because Slower manual releases
* Sources: `d:25`, `v:25.3`
