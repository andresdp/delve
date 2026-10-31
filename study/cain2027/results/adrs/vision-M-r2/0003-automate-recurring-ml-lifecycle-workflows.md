# Automate recurring ML lifecycle workflows

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining and pushing models to devices create recurring operational work for a small team. The design space contrasts lifecycle automation with manual script-driven execution.

## Decision Drivers

* Small team
* Weekly model updates
* Tight infrastructure budget

## Considered Options

* Automated ML lifecycle workflows (`v:38.1`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Automated ML lifecycle workflows" (`v:38.1`).

Automation fits the recurring weekly cycle and limited team capacity. “MLOps Principles” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support lifecycle automation; the checked rival combined a service deployment, drift trigger, and DataOps-centered toolchain, which does not match the offline and weekly requirements as directly.

### Consequences

* Build a repeatable path from training through device rollout.
* Keep workflow scope small to control infrastructure and maintenance costs.

## Pros and Cons of the Options

### Automated ML lifecycle workflows

* Good, because Reduces repeated work
* Good, because Covers deployment operations
* Bad, because Requires workflow setup
* Sources: `s01_p06`, `s04_p18`, `s10_p03`, `s18_p04`, `s18_p06`, `s22_p03`, `s22_p04`, `s25_p01`, `s29_p02`

### Manual script-driven workflow

* Good, because Low initial setup
* Good, because Simple to start
* Bad, because Repeated operator effort
* Bad, because Error-prone handoffs
* Sources: `s04_p02`, `s09_p08`, `s18_p06`, `s20_p12`, `s21_p07`, `s24_p09`, `s24_p10`
