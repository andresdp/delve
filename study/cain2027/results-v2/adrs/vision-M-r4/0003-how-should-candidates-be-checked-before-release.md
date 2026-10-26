# How should candidates be checked before release?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces a candidate that may replace the model running on cameras. A repeatable quality check is needed before promotion.

## Decision Drivers

* Weekly model updates
* Production quality
* Small team

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Production quality decides the choice: evaluate each weekly candidate against held-out labelled data before promotion. This gives up the broader comparison of multiple candidates described by metric-driven evaluation; the two values can also be combined, and the design space marks evaluation choices as affecting production monitoring outcomes.

### Consequences

* Maintain a held-out dataset separate from training data.
* Define a promotion rule using inspection-quality metrics.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Weekly updates: repeatable evaluation before deployment
* Good, because Production quality: tests candidates against held-out data
* Bad, because Small team: requires a maintained evaluation pipeline
* Bad, because Production quality: depends on representative held-out data
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`, `s09_p04`, `s20_p03`, `s22_p08`, `s25_p09`

### Metric-driven candidate model evaluation

* Good, because Production quality: compares candidates on selected metrics
* Good, because Small team: makes promotion criteria explicit
* Bad, because Weekly updates: still needs a maintained evaluation process
* Bad, because Production quality: metric choice may miss other defects
* Sources: `s02_p09`, `s09_p04`, `s09_p07`, `s19_p05`, `s22_p06`, `s22_p15`, `s25_p09`
