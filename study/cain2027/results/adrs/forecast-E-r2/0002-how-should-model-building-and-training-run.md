# How should model building and training run?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without disrupting the weekly run. An automated build pipeline can handle training, evaluation, and validation. [d:18, v:18.1]

## Decision Drivers

* Quick experimentation
* Weekly run stability
* Small team

## Considered Options

* Model building pipeline (`v:18.1`)
* Model builder component (`v:18.2`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Model building pipeline" (`v:18.1`).

An automated pipeline creates a repeatable route for training, evaluation, and validation, making it easier to advance model ideas without modifying the weekly forecast run directly. [d:18, v:18.1]

### Consequences

* Model changes pass through the pipeline before release.
* The team maintains pipeline definitions and evaluation steps.

## Pros and Cons of the Options

### Model building pipeline

* Good, because Automates evaluation and validation
* Good, because Repeatable runs
* Bad, because Requires pipeline upkeep
* Sources: `d:18`, `v:18.1`

### Model builder component

* Good, because Dedicated building component
* Bad, because Pipeline coordination needed
* Sources: `d:18`, `v:18.2`

### Model building in development tool

* Good, because Fast local iteration
* Bad, because Less repeatable production path
* Sources: `d:18`, `v:18.3`
