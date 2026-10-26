# How should workflow steps run?

* System: Retail demand forecasting

## Context and Problem Statement

The pipeline must produce weekly forecasts reliably while allowing the team to change models. Manual coordination is possible but places each run’s consistency on the team.

## Decision Drivers

* Weekly run safety
* Fast model iteration
* Small team

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Weekly run safety decides: an orchestrated pipeline makes stages repeatable and easier to rerun as model ideas change. This accepts added orchestration upkeep; “Architecting a Machine Learning Pipeline” and “MLOps: Continuous delivery and automation pipelines in machine learning” describe connected, repeatable stages.

### Consequences

* Pipeline stages and dependencies need maintenance.
* Changes can be evaluated through a repeatable workflow.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Weekly run safety: repeatable connected stages
* Good, because Fast iteration: re-run changed stages
* Bad, because Small team: orchestration adds setup and upkeep
* Sources: `s02_p09`, `s04_p07`, `s04_p15`, `s04_p17`, `s04_p18`, `s06_p07`, `s06_p13`, `s06_p15`, `s08_p01`, `s08_p02`, `s09_p07`, `s09_p08`, `s10_p07`, `s17_p05`, `s17_p06`, `s19_p05`, `s19_p09`, `s20_p05`, `s20_p10`, `s21_p10`, `s25_p01`, `s25_p02`, `s25_p09`, `s28_p03`

### Manual script-driven workflow

* Good, because Small team: low initial tooling burden
* Bad, because Weekly run safety: depends on manual consistency
* Bad, because Fast iteration: coordination slows repeat runs
* Sources: `s04_p02`, `s09_p08`, `s18_p06`, `s20_p12`, `s21_p07`, `s24_p09`, `s24_p10`
