# How to monitor classification quality

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space distinguishes model performance monitoring from logging data and predictions; a checked design point flagged these as alternatives in one dimension.

## Decision Drivers

* Detect quality drift
* High throughput at scale

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Detect quality drift decides: directly monitoring model performance serves the stated need. We give up the additional diagnostic detail available from retaining and monitoring inputs and predictions.

### Consequences

* Define performance measures and alert thresholds.
* Monitoring does not by itself specify how to correct drift.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Drift visibility: observes model performance
* Bad, because Throughput: metrics must be aggregated at scale
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Diagnosis: records inputs and predictions
* Bad, because Cost: data volume to retain and inspect
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Drift visibility: quality changes go unseen
* Sources: `d:22`, `v:22.3`
