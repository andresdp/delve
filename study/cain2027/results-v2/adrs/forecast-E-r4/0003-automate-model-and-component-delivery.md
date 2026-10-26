# Automate model and component delivery

* System: Retail demand forecasting

## Context and Problem Statement

Model ideas should reach production quickly, but releases must not break the weekly run. The design space covers CI/CD scope and testing, but not a specific release safety mechanism.

## Decision Drivers

* 1. Fast model iteration
* 2. Protect weekly run
* 3. Small team

## Considered Options

* Build, test, and deploy models to be served and other system components (`v:25.1`)
* Build, test, and deploy machine learning pipelines and components needed during pipeline runs (`v:25.2`)
* No automated deployment (`v:25.3`)

## Decision Outcome

Chosen option: "Build, test, and deploy models to be served and other system components" (`v:25.1`).

Fast model iteration decides the choice: automate delivery of models and system components. This gives up some simplicity and makes release checks essential to protect the weekly run.

### Consequences

* Include model and serving components in the automated delivery path.
* Define release checks and recovery behavior; the brief does not specify them.

## Pros and Cons of the Options

### Build, test, and deploy models to be served and other system components

* Good, because Fast iteration: automates model delivery
* Bad, because Protect weekly run: deployment needs strong checks
* Sources: `d:25`, `v:25.1`

### Build, test, and deploy machine learning pipelines and components needed during pipeline runs

* Good, because Protect weekly run: automates pipeline component delivery
* Bad, because Fast iteration: does not explicitly cover served models
* Sources: `d:25`, `v:25.2`

### No automated deployment

* Bad, because Fast iteration: manual releases slow model ideas
* Sources: `d:25`, `v:25.3`
