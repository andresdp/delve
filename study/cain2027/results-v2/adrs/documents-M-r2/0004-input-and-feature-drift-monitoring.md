# Input and feature-drift monitoring

*How should production quality and drift be monitored?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility when classification quality drifts. The brief does not state how quickly labels or quality measurements become available.

## Decision Drivers

* Drift visibility
* Classification quality

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Drift visibility decides the choice: input monitoring gives operators a signal about changing document data, as described in “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Continuous delivery and automation pipelines in machine learning.” It cannot establish that accuracy has fallen, so prediction quality should also be measured when labels become available.

### Consequences

* Track input distributions and schema changes.
* Retain predictions and eventual labels for quality checks.
* Define which drift signals require investigation.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Drift visibility: detects changes in inputs and distributions
* Bad, because Classification quality: drift does not prove accuracy loss
* Sources: `s04_p03`, `s06_p02`, `s23_p03`

### Real-time prediction-quality monitoring

* Good, because Classification quality: measures model behavior when labels are available
* Bad, because Drift visibility: quality signal may arrive late
* Sources: `s01_p06`, `s04_p12`, `s23_p04`

### Passive production operation

* Good, because Cost: little monitoring infrastructure
* Bad, because Drift visibility: operators may miss degradation
* Sources: `s04_p02`, `s20_p02`
