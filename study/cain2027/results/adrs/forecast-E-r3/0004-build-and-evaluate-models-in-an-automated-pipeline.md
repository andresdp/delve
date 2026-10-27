# Build and evaluate models in an automated pipeline

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without disrupting the weekly run. The design space contrasts an automated model-building pipeline with a dedicated component and development-tool-only model building (d:18).

## Decision Drivers

* Fast model iteration
* Protected weekly run
* Reproducibility

## Considered Options

* Model building pipeline (`v:18.1`)
* Model builder component (`v:18.2`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Model building pipeline" (`v:18.1`).

Automating training, evaluation, and validation provides a repeatable path from an experiment to a production candidate (d:18, v:18.1). The design-point check returned no warnings, but no attesting sources; the combination is novel in this workspace.

### Consequences

* Promote candidates through a controlled release step.
* Maintain pipeline definitions as model workflows evolve.

## Pros and Cons of the Options

### Model building pipeline

* Good, because Automates training and evaluation
* Good, because Repeatable model workflow
* Bad, because Pipeline requires maintenance
* Sources: `d:18`, `v:18.1`

### Model builder component

* Good, because Reusable training component
* Bad, because Workflow orchestration remains separate
* Sources: `d:18`, `v:18.2`

### Model building in development tool

* Good, because Convenient experimentation
* Bad, because Harder to reproduce production runs
* Sources: `d:18`, `v:18.3`
