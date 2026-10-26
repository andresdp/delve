# Monitor production forecasts

* System: Retail demand forecasting

## Context and Problem Statement

A broken weekly run would undermine the system, and new models will be released over time. The brief does not state what production signals to track.

## Decision Drivers

* 1. Protect weekly run
* 2. Fast model iteration

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Monitoring or logging data and predictions" (`v:22.2`).

Protecting the weekly run decides the choice: logging data and predictions provides operational visibility even when forecast outcomes are not yet known. The cost is storing and reviewing those records.

### Consequences

* Retain forecast inputs and outputs for operational review.
* Choose retention, alerting, and privacy rules; the brief does not specify them.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Protect weekly run: observes model performance
* Bad, because Fast iteration: needs performance measures and labels
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Protect weekly run: records inputs and outputs
* Bad, because Small team: adds log storage and review work
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Protect weekly run: failures may go unnoticed
* Sources: `d:22`, `v:22.3`
