# Scheduled staged pipeline

*How should the weekly pipeline run?*

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts are produced weekly for every store and product, and the weekly run must remain dependable as the team iterates. A scheduled, staged pipeline makes the run repeatable and separates failures by step.

## Decision Drivers

* weekly cadence
* run reliability
* small team ownership

## Considered Options

* Scheduled staged pipeline
* Single end-to-end script
* Event-driven services

## Decision Outcome

Chosen option: "Scheduled staged pipeline".

The weekly cadence suits a scheduled workflow with explicit data preparation, training or model selection, forecasting, and publication stages. Stage boundaries support diagnosis and recovery without coupling experiments to the production run.

### Consequences

* Add orchestration and run monitoring.
* Make stages safe to rerun.
* Track run status and outputs.

## Pros and Cons of the Options

### Scheduled staged pipeline

* Good, because clear step boundaries
* Good, because repeatable runs
* Bad, because requires orchestration
* Bad, because more setup

### Single end-to-end script

* Good, because simple to start
* Good, because few components
* Bad, because harder to recover
* Bad, because experiments can disrupt runs

### Event-driven services

* Good, because independent scaling
* Good, because flexible triggers
* Bad, because more operational overhead
* Bad, because unneeded complexity
