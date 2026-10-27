# Weekly workflow coordination

* System: Retail demand forecasting

## Context and Problem Statement

A scheduled weekly forecast needs repeatable stages that can run without hand-coordinated transitions. New model ideas should fit into the same workflow.

## Decision Drivers

* Reliable weekly run
* Rapid experimentation
* Three-person team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

A pipeline makes weekly preparation, training, evaluation, and promotion repeatable while providing a path for new candidates. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” describe this approach; the manual workflow is described as suitable for infrequently changing models in “Productionizing Machine Learning with a Microservices Architecture.”

### Consequences

* Define and version pipeline stages.
* Make the weekly run observable and restartable.
* Choose a data-ingestion mechanism before finalizing orchestration; the design-space point flags this dependency.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable staged execution
* Good, because Supports evaluation and deployment
* Bad, because Requires orchestration upkeep
* Sources: `s02_p09`, `s04_p07`, `s04_p15`, `s04_p17`, `s04_p18`, `s06_p07`, `s06_p13`, `s06_p15`, `s08_p01`, `s08_p02`, `s09_p07`, `s09_p08`, `s10_p07`, `s17_p05`, `s17_p06`, `s19_p05`, `s19_p09`, `s20_p05`, `s20_p10`, `s21_p10`, `s25_p01`, `s25_p02`, `s25_p09`, `s28_p03`

### Manual script-driven workflow

* Good, because Low initial setup
* Good, because Direct operator control
* Bad, because Manual handoffs
* Bad, because Poor fit for recurring runs
* Sources: `s04_p02`, `s09_p08`, `s18_p06`, `s20_p12`, `s21_p07`, `s24_p09`, `s24_p10`
