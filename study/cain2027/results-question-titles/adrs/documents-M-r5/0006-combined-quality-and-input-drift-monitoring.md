# Combined quality and input-drift monitoring

*How should production quality be monitored?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Input drift can provide an early signal, while direct quality measures depend on labeled outcomes becoming available.

## Decision Drivers

* Visible quality drift
* Operational awareness

## Considered Options

* Combined quality and input-drift monitoring
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Combined quality and input-drift monitoring".

Combine real-time prediction-quality monitoring with input and feature-drift monitoring. The decision has zero exclusivity, so its values are combinable; “How to power up your product by machine learning with python microservice, pt. 1,” “Productionizing Machine Learning with a Microservices Architecture,” and “MLOps: Continuous delivery and automation pipelines in machine learning” support monitoring. The checked combination is unattested.

### Consequences

* Track quality when labeled outcomes are available.
* Set drift thresholds and alert ownership.

## Pros and Cons of the Options

### Combined quality and input-drift monitoring

* Good, because Tracks quality and changing inputs
* Good, because Can reveal issues before labels arrive
* Bad, because Needs labels for direct quality measures
* Bad, because Adds monitoring and alerting work
* Sources: `s01_p06`, `s04_p03`, `s06_p08`

### Passive production operation

* Good, because Lower monitoring effort
* Good, because Simple to operate
* Bad, because Quality drift may go unnoticed
* Bad, because No active performance tracking
* Sources: `s13_p10`, `s23_p13`
