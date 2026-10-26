# Production quality and drift monitoring

* System: Large-scale document classification

## Context and Problem Statement

The classifier must expose quality drift to operators after deployment. Labels may arrive later, so monitoring needs to observe input changes as well as prediction quality.

## Decision Drivers

* Detect quality drift
* Operator visibility
* Delayed labels

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Choose input monitoring because the brief explicitly requires drift visibility, including when labels are delayed. Practitioners describe this in “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Continuous delivery and automation pipelines in machine learning.”

### Consequences

* Operators need to review drift alerts.
* Define baselines and alert thresholds.
* Quality impact still needs validation when labels arrive.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Flags changing inputs
* Good, because Works before labels arrive
* Bad, because Drift may not mean quality loss
* Bad, because Requires baseline management
* Sources: `s04_p03`, `s06_p02`, `s23_p03`

### Real-time prediction-quality monitoring

* Good, because Tracks model behavior
* Good, because Direct quality signal
* Bad, because Needs timely labels
* Bad, because May miss input changes
* Sources: `s04_p02`, `s06_p06`, `s23_p04`

### Passive production operation

* Good, because Minimal monitoring effort
* Bad, because No drift visibility
* Bad, because Failures may go unnoticed
