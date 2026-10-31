# Production quality and drift monitoring

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility when classification quality drifts. Monitoring can combine practices: this design-space dimension has zero exclusivity, and the checked point warns that it permits only one value per dimension.

## Decision Drivers

* quality drift visibility
* operational oversight

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Choose drift monitoring to give operators visibility into changing inputs, and combine it with prediction-quality monitoring when labels become available. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Continuous delivery and automation pipelines in machine learning” support drift monitoring; “Machine Learning Monitoring: What It Is, and What We Are Missing” supports quality monitoring.

### Consequences

* Monitor input and feature changes in production.
* Assess prediction quality when ground-truth labels arrive.
* The checked design point flags the combined monitoring values as a same-dimension warning.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because detects changing inputs
* Good, because reveals data shifts
* Bad, because drift alone does not measure quality
* Sources: `s04_p03`, `s06_p02`, `s23_p03`

### Real-time prediction-quality monitoring

* Good, because tracks prediction behavior
* Good, because surfaces quality changes
* Bad, because depends on label availability
* Sources: `s04_p02`, `s06_p06`, `s23_p04`

### Passive production operation

* Good, because requires little monitoring setup
* Bad, because does not track quality
* Sources: `s13_p10`, `s23_p13`
