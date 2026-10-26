# How should inference be packaged and deployed?

* System: Large-scale document classification

## Context and Problem Statement

The classifier must process large and variable workloads, and the brief does not specify a particular cloud or runtime. A portable package supports scaling across managed or self-managed infrastructure.

## Decision Drivers

* Daily volume
* Seasonal demand swings
* Reproducible deployment

## Considered Options

* Containerized inference deployment (`v:30.19`)
* Model-as-dependency deployment (`v:30.18`)

## Decision Outcome

Chosen option: "Containerized inference deployment" (`v:30.19`).

Seasonal scaling and reproducible deployment decide the choice: “MLOps: Continuous Delivery and Automation Pipelines in Machine Learning” describes containerized inference across runtimes. This adds container operations compared with bundling the model into each application; the checked point had no warnings but was unattested.

### Consequences

* Inference images and dependencies must be versioned and maintained.
* Runtime placement remains open to managed, on-premise, or hybrid infrastructure.

## Pros and Cons of the Options

### Containerized inference deployment

* Good, because Reproducible deployment: packages code and dependencies
* Good, because Seasonal demand: deploys across managed or hybrid runtimes
* Bad, because Compute cost: container infrastructure needs operation
* Sources: `s04_p02`, `s06_p07`, `s07_p03`, `s19_p17`

### Model-as-dependency deployment

* Good, because Reproducible deployment: model ships with consuming application
* Bad, because Seasonal demand: scaling is coupled to the application
* Sources: `s01_p05`, `s02_p10`, `s09_p09`, `s19_p13`, `s19_p14`, `s19_p15`, `s21_p05`, `s21_p18`, `s25_p01`, `s25_p06`
