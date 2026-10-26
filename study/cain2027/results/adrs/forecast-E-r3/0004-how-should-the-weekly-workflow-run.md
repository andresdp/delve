# How should the weekly workflow run?

* System: Retail demand forecasting

## Context and Problem Statement

A reliable weekly forecast requires repeatable data preparation and model building. The team also needs new ideas to reach production quickly.

## Decision Drivers

* Weekly run
* Reproducibility
* Fast iteration

## Considered Options

* Scheduled data and model building pipelines (`v:12.3`)
* On-demand trigger (`v:12.1`)
* Model building in development tool (`v:18.3`)

## Decision Outcome

Chosen option: "Scheduled data and model building pipelines".

Schedule the workflow weekly and use automated data and model building pipelines to make runs repeatable while keeping experimentation connected to production (d:12, v:12.3; d:14, v:14.1; d:18, v:18.1).

### Consequences

* Pipeline stages need maintained code and configuration.
* On-demand reruns remain useful for recovery.

## Pros and Cons of the Options

### Scheduled data and model building pipelines

* Good, because Automates weekly work
* Good, because Repeatable stages
* Bad, because Needs orchestration ownership
* Sources: `d:12`, `v:12.3`, `d:14`, `v:14.1`, `d:18`, `v:18.1`

### On-demand trigger

* Good, because Simple to start
* Good, because Useful for reruns
* Bad, because Weekly run depends on people
* Sources: `d:12`, `v:12.1`

### Model building in development tool

* Good, because Fast experimentation
* Bad, because Run consistency harder
* Sources: `d:18`, `v:18.3`
