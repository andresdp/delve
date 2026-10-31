# Automate data preparation in a pipeline

* System: Retail demand forecasting

## Context and Problem Statement

Weekly runs need repeatable processing, while the three-person team needs a workflow that can be rerun as model ideas change. The design space compares a data pipeline with ETL, a dedicated component, and no automation (d:14).

## Decision Drivers

* Repeatable weekly runs
* Three-person team
* Fast iteration

## Considered Options

* Data pipeline (`v:14.1`)
* ETL pipeline (`v:14.2`)
* Data processing component (`v:14.3`)
* No data processing automation (`v:14.4`)

## Decision Outcome

Chosen option: "Data pipeline" (`v:14.1`).

A dedicated flexible pipeline makes recurring data preparation repeatable and supports rapid model iteration (d:14, v:14.1). The design-point check returned no warnings, but no attesting sources; the combination is novel in this workspace.

### Consequences

* Keep transformations under version control.
* Pipeline changes need review and maintenance.

## Pros and Cons of the Options

### Data pipeline

* Good, because Dedicated repeatable workflow
* Good, because Flexible processing stages
* Bad, because Requires pipeline upkeep
* Sources: `d:14`, `v:14.1`

### ETL pipeline

* Good, because Clear extract-transform-load stages
* Bad, because May constrain other processing steps
* Sources: `d:14`, `v:14.2`

### Data processing component

* Good, because Encapsulates processing logic
* Bad, because Orchestration remains separate
* Sources: `d:14`, `v:14.3`

### No data processing automation

* Good, because Low initial setup
* Bad, because Manual repetition and drift
* Sources: `d:14`, `v:14.4`
