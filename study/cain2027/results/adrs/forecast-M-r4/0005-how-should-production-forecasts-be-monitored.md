# How should production forecasts be monitored?

* System: Retail demand forecasting

## Context and Problem Statement

A weekly forecast can degrade as inputs or demand patterns change. The system needs visibility to detect problems before relying on a faulty forecast set.

## Decision Drivers

* forecast quality
* input changes
* weekly operations

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Periodic model health checks (`v:6.18`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Input and feature checks can flag a changed weekly data profile and prompt investigation before forecast use. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps Principles” support monitoring changes in features; drift alone does not establish forecast accuracy, so quality evaluation remains an uncovered design detail.

### Consequences

* Define expected input schemas and profiles.
* Investigate drift before changing the production model.
* Add forecast quality checks when labels become available.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because detects changing inputs
* Good, because supports investigation
* Bad, because drift is not quality
* Bad, because thresholds need tuning
* Sources: `s04_p03`, `s06_p08`, `s22_p11`

### Periodic model health checks

* Good, because fits recurring cadence
* Good, because lower continuous monitoring load
* Bad, because issues may be found later
* Bad, because requires review effort
* Sources: `s06_p02`, `s23_p08`, `s24_p07`
