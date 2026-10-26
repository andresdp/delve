# How should model building be organized?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly, while the weekly run must remain dependable.

## Decision Drivers

* Fast iteration
* Reliable weekly run

## Considered Options

* Model building pipeline (`v:18.1`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Model building pipeline" (`v:18.1`).

An automated model building pipeline supports repeatable training and validation while giving the small team a consistent path for new ideas (d:18, v:18.1).

### Consequences

* Model changes follow a defined build workflow.
* Pipeline components need upkeep.

## Pros and Cons of the Options

### Model building pipeline

* Good, because Automates training and validation
* Good, because Repeatable model builds
* Bad, because Pipeline maintenance
* Sources: `d:18`, `v:18.1`

### Model building in development tool

* Good, because Flexible experimentation
* Bad, because Less repeatable builds
* Sources: `d:18`, `v:18.3`
