# Production quality and drift monitoring

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space treats monitoring practices as combinable, and the brief does not say when labels become available.

## Decision Drivers

* Drift visibility
* Quality visibility
* Operator response

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Periodic model health checks (`v:6.18`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Drift visibility decides the initial choice because the brief explicitly requires operators to see quality drift, and input shifts can be monitored without assuming immediate labels. This gives up direct confirmation of prediction quality; “MLOps: Continuous delivery and automation pipelines in machine learning” and “Machine Learning Monitoring: What It Is, and What We Are Missing” describe drift monitoring. Pair it with quality monitoring once label availability is established.

### Consequences

* Monitor input and feature distributions over time.
* Define alert thresholds and operator follow-up.
* Add label-based quality measurement when labels are available.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Drift visibility: detects changes in inputs and feature distributions
* Good, because Operator response: can surface shifts before labels arrive
* Bad, because Quality visibility: drift does not prove classification errors
* Bad, because Operator response: thresholds and follow-up need configuration
* Sources: `s04_p03`, `s04_p05`, `s04_p12`, `s06_p02`, `s06_p08`, `s20_p03`, `s21_p10`, `s22_p11`, `s23_p03`, `s23_p04`, `s23_p05`, `s24_p01`, `s24_p07`, `s24_p08`, `s24_p11`, `s25_p01`

### Real-time prediction-quality monitoring

* Good, because Quality visibility: measures model behavior and prediction quality
* Good, because Operator response: gives direct evidence of degradation
* Bad, because Drift visibility: does not by itself explain input changes
* Bad, because Quality visibility: depends on ground-truth labels being available
* Sources: `s01_p06`, `s04_p02`, `s04_p12`, `s06_p06`, `s06_p13`, `s08_p02`, `s13_p10`, `s18_p01`, `s20_p02`, `s20_p03`, `s22_p11`, `s23_p03`, `s23_p04`, `s23_p05`, `s23_p08`, `s23_p11`, `s24_p01`, `s24_p05`, `s24_p07`, `s24_p08`, `s24_p11`

### Periodic model health checks

* Good, because Operator response: supports recurring review
* Good, because Quality visibility: can assess model health over time
* Bad, because Drift visibility: changes may go unnoticed between checks
* Bad, because Quality visibility: slower signal than continuous measurement
