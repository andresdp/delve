# How should model building and training run?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly while protecting the weekly run; the design space covers automated model building (d:18) and batch training (d:19).

## Decision Drivers

* Fast iteration
* Weekly run reliability
* Small team

## Considered Options

* Model building pipeline with batch-based learning (`v:18.1 / v:19.1`)
* Model builder component with incremental learning (`v:18.2 / v:19.2`)
* Model building in development tool with batch-based learning (`v:18.3 / v:19.1`)

## Decision Outcome

Chosen option: "Model building pipeline with batch-based learning" (`v:18.1 / v:19.1`).

Weekly run reliability decides the choice: automate offline training and validation before promotion, accepting the initial pipeline setup to make model iteration repeatable.

### Consequences

* Keep experiments and production training reproducible from versioned inputs.
* Gate promotion on evaluation and validation results.

## Pros and Cons of the Options

### Model building pipeline with batch-based learning

* Good, because Fast iteration: automate training, evaluation, and validation
* Good, because Weekly run reliability: train offline in repeatable batches
* Bad, because Small team: pipeline needs setup and ownership
* Sources: `d:18`, `v:18.1`, `d:19`, `v:19.1`

### Model builder component with incremental learning

* Good, because Fast iteration: isolated builder supports model changes
* Bad, because Weekly run reliability: incremental updates add production state
* Bad, because Small team: component integration needs ownership
* Sources: `d:18`, `v:18.2`, `d:19`, `v:19.2`

### Model building in development tool with batch-based learning

* Good, because Small team: familiar development workflow
* Bad, because Fast iteration: manual promotion can slow release
* Bad, because Weekly run reliability: less automated validation
* Sources: `d:18`, `v:18.3`, `d:19`, `v:19.1`
