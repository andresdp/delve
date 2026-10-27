# Orchestrate the weekly ML workflow as a repeatable pipeline

* System: Retail demand forecasting

## Context and Problem Statement

The same data preparation, training, evaluation, and scoring steps must run each week, and new ideas should enter production without making that run fragile.

## Decision Drivers

* Weekly repeatability
* Small team
* Fast iteration

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

An orchestrated pipeline provides repeatable stages for preparation, training, evaluation, and scoring, which suits the weekly cadence and small team. “MLOps: Continuous delivery and automation pipelines in machine learning” describes pipeline orchestration across these stages (s06_p07, s06_p15).

### Consequences

* Pipeline stages and dependencies need maintenance.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Repeatable connected stages
* Good, because Automates recurring work
* Bad, because Requires pipeline upkeep
* Sources: `s02_p09`, `s04_p07`, `s04_p15`, `s04_p17`, `s04_p18`, `s06_p07`, `s06_p13`, `s06_p15`, `s08_p01`, `s08_p02`, `s09_p07`, `s09_p08`, `s10_p07`, `s17_p05`, `s17_p06`, `s19_p05`, `s19_p09`, `s20_p05`, `s20_p10`, `s21_p10`, `s25_p01`, `s25_p02`, `s25_p09`, `s28_p03`

### Manual script-driven workflow

* Good, because Simple to start
* Good, because Direct team control
* Bad, because Manual transitions
* Bad, because Less suited to frequent changes
* Sources: `s04_p02`, `s09_p08`, `s18_p06`, `s20_p12`, `s21_p07`, `s24_p09`, `s24_p10`
