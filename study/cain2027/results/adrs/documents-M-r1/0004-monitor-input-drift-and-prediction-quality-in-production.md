# Monitor input drift and prediction quality in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility into quality drift. Inputs may shift before delayed labels make prediction quality measurable, so monitoring should cover both signals.

## Decision Drivers

* Quality drift visibility
* Operational oversight
* Changing input distributions

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Use input drift as the primary early signal and add quality monitoring where labels become available; the monitoring dimension has low exclusivity, so these practices can be combined. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Machine Learning Monitoring: What It Is, and What We Are Missing” discuss drift and quality monitoring.

### Consequences

* Retain suitable input statistics for comparison.
* Set thresholds and an investigation process.
* Connect delayed labels to later quality assessment.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Can surface input changes
* Good, because Supports early investigation
* Bad, because Drift does not prove quality loss
* Bad, because Requires baselines and alert thresholds
* Sources: `s04_p03`, `s06_p02`, `s23_p03`

### Real-time prediction-quality monitoring

* Good, because Tracks model behavior
* Good, because Connects monitoring to quality
* Bad, because Needs timely labels
* Bad, because Quality calculation may lag predictions
* Sources: `s06_p06`, `s23_p04`

### Passive production operation

* Good, because Low monitoring overhead
* Good, because Simple operation
* Bad, because Drift can remain unseen
* Bad, because Conflicts with operator visibility need
