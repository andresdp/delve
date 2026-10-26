# Develop model ideas iteratively

* System: Retail demand forecasting

## Context and Problem Statement

A three-person team owns the pipeline end to end and wants new ideas to reach production quickly. Short development cycles align with that goal, while the weekly run creates a need to validate changes as they progress.

## Decision Drivers

* Fast model iteration
* Weekly run stability

## Considered Options

* Lean iterative ML development (`v:40.1`)
* Waterfall or V-model process (`v:40.6`)

## Decision Outcome

Chosen option: "Lean iterative ML development" (`v:40.1`).

Fast model iteration decides the choice: short cycles help the small team move model ideas forward. “MLOps Principles” and “MLOps: Continuous delivery and automation pipelines in machine learning” support iterative delivery; the cost is validating frequent changes against the weekly run.

### Consequences

* Deliver model changes in small increments.
* Keep release checks aligned with the weekly run.

## Pros and Cons of the Options

### Lean iterative ML development

* Good, because Fast model iteration: delivers through short cycles
* Bad, because Weekly run stability: frequent changes need validation
* Sources: `s01_p06`, `s01_p08`, `s06_p06`, `s06_p15`, `s13_p07`, `s17_p03`, `s21_p02`, `s22_p01`

### Waterfall or V-model process

* Good, because Weekly run stability: defines sequential process stages
* Bad, because Fast model iteration: sources reject heavyweight sequencing
