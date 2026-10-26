# Forecast workflow coordination

* System: Retail demand forecasting

## Context and Problem Statement

Weekly store and product forecasts need repeatable stages, while new model ideas should reach production quickly. The workflow must make a missed or failed stage visible before it disrupts the weekly run.

## Decision Drivers

* Past-week reproducibility
* Fast model iteration
* Protect weekly run

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Past-week reproducibility and protection of the weekly run decide the choice: orchestration makes the stages repeatable. It costs more setup than manual scripts.

### Consequences

* Pipeline stages and dependencies need maintenance.
* Failures can be isolated to stages for reruns.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Reproducibility: repeatable stages
* Good, because Fast iteration: connected training and evaluation
* Bad, because Setup cost: orchestration overhead
* Sources: `s02_p09`, `s06_p07`

### Manual script-driven workflow

* Good, because Fast start: simple scripts
* Bad, because Reproducibility: manual transitions
* Bad, because Protect weekly run: more operator-dependent
* Sources: `s04_p02`
