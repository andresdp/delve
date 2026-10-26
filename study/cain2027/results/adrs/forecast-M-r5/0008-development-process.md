# Development process

* System: Retail demand forecasting

## Context and Problem Statement

Three data scientists own the end-to-end pipeline, so the process should allow rapid model exploration without relying on separate specialist teams for every change.

## Decision Drivers

* Small team
* Fast model ideas
* End-to-end ownership

## Considered Options

* Lean iterative ML development (`v:40.1`)
* Standardized ML process model (`v:40.4`)

## Decision Outcome

Chosen option: "Lean iterative ML development" (`v:40.1`).

Short iterations let the team explore model ideas while the shared pipeline and release gates protect the recurring run. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” support iterative delivery; the checked point has no warnings but is unattested.

### Consequences

* Keep experiments small and reviewable.
* Automated pipeline checks carry part of the safety burden.

## Pros and Cons of the Options

### Lean iterative ML development

* Good, because Short learning cycles
* Good, because Fits evolving models
* Bad, because Needs automated checks
* Bad, because Can strain team capacity
* Sources: `s01_p06`, `s01_p08`, `s06_p06`, `s06_p15`, `s13_p07`, `s17_p03`, `s21_p02`, `s22_p01`

### Standardized ML process model

* Good, because Consistent steps
* Good, because Templates guide work
* Bad, because May add process overhead
* Bad, because Less adaptable
