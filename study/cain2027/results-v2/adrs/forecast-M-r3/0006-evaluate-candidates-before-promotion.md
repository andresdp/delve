# Evaluate candidates before promotion

* System: Retail demand forecasting

## Context and Problem Statement

Model ideas need a reliable route to production that protects the weekly run. The design space describes held-out offline evaluation as a promotion check and threshold testing as a separate regression practice.

## Decision Drivers

* Weekly run stability
* Fast model iteration

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)
* Previously-built-model diff testing (`v:13.3`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Weekly run stability decides the choice: evaluate candidates against held-out data before promotion. Sources including “MLOps Principles” and “MLOps: Continuous delivery and automation pipelines in machine learning” support offline evaluation; this adds a check to the delivery path.

### Consequences

* Maintain held-out data and evaluation steps.
* Promotion waits for evaluation results.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Weekly run stability: checks candidates before deployment
* Bad, because Fast model iteration: evaluation adds a promotion step
* Sources: `s02_p09`, `s04_p15`, `s06_p02`, `s09_p04`, `s20_p03`, `s20_p09`, `s22_p08`, `s25_p09`

### Metric-driven candidate model evaluation

* Good, because Fast model iteration: compares candidates on selected metrics
* Bad, because Weekly run stability: does not alone define a held-out deployment check
* Sources: `s09_p04`, `s17_p04`, `s19_p05`, `s22_p06`, `s22_p15`, `s23_p09`, `s25_p09`

### Previously-built-model diff testing

* Good, because Weekly run stability: compares a candidate with an existing model
* Bad, because Fast model iteration: sources report maintenance difficulty
