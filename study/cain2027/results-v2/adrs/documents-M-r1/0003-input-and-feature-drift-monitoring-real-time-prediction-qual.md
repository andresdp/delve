# Input and feature-drift monitoring + real-time prediction-quality monitoring

*How should classification quality drift be detected?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space treats monitoring practices as combinable, so use input drift signals alongside measured prediction quality when labels become available.

## Decision Drivers

* Drift visibility
* Quality feedback

## Considered Options

* Input and feature-drift monitoring + real-time prediction-quality monitoring
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring + real-time prediction-quality monitoring".

Drift visibility decides the choice: input monitoring can reveal changes before delayed labels arrive, while prediction-quality monitoring checks outcomes once labels are available. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Machine Learning Monitoring: What It Is, and What We Are Missing” describe these monitoring practices; the trade-off is added monitoring work and delayed quality feedback.

### Consequences

* Retain inputs and predictions for monitoring and later evaluation.
* Define alert thresholds and a response process.

## Pros and Cons of the Options

### Input and feature-drift monitoring + real-time prediction-quality monitoring

* Good, because Drift visibility: flags changing inputs and schemas
* Good, because Quality feedback: measures predictions when labels arrive
* Bad, because Quality feedback: waits for labeled examples
* Bad, because Operations: requires monitoring both inputs and predictions
* Sources: `s04_p03`, `s06_p02`, `s23_p03`, `s23_p04`

### Passive production operation

* Good, because Operations: minimal monitoring work
* Bad, because Drift visibility: no active tracking
* Bad, because Quality feedback: failures may remain unnoticed
* Sources: `s13_p10`, `s21_p07`, `s23_p13`
