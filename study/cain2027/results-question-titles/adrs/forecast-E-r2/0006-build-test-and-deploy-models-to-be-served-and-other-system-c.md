# Build, test, and deploy models to be served and other system components

*What should CI/CD build and deploy?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must move quickly while protecting the weekly run. Automating model and system component delivery supports a repeatable release path. [d:25, v:25.1]

## Decision Drivers

* Fast model releases
* Weekly run stability

## Considered Options

* Build, test, and deploy models to be served and other system components (`v:25.1`)
* Build, test, and deploy machine learning pipelines and components needed during pipeline runs (`v:25.2`)
* No automated deployment (`v:25.3`)

## Decision Outcome

Chosen option: "Build, test, and deploy models to be served and other system components" (`v:25.1`).

Automating model delivery gives the team a faster, repeatable route to production while preserving a controlled release step before the weekly run uses a new model. [d:25, v:25.1]

### Consequences

* Deployment automation needs maintenance.
* Release checks should complete before production use.

## Pros and Cons of the Options

### Build, test, and deploy models to be served and other system components

* Good, because Automates model delivery
* Good, because Repeatable deployment
* Bad, because Requires deployment automation
* Sources: `d:25`, `v:25.1`

### Build, test, and deploy machine learning pipelines and components needed during pipeline runs

* Good, because Automates pipeline delivery
* Bad, because Does not by itself automate model release
* Sources: `d:25`, `v:25.2`

### No automated deployment

* Good, because Minimal automation setup
* Bad, because Slower, manual releases
* Sources: `d:25`, `v:25.3`
