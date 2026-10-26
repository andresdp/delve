# Workflow execution: orchestrated pipeline or manual scripts?

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasts need a repeatable path from data preparation through evaluation, while new model ideas should reach production quickly. Prioritized requirements: (1) reproduce past-week forecasts, (2) protect the weekly run, (3) shorten the path for model changes; the three-person team favors a manageable operating burden.

## Decision Drivers

* Past-week reproducibility
* Weekly-run reliability
* Fast model iteration

## Considered Options

* Orchestrated ML pipeline (`v:32.2`)
* Manual script-driven workflow (`v:32.1`)

## Decision Outcome

Chosen option: "Orchestrated ML pipeline" (`v:32.2`).

Past-week reproducibility and weekly-run reliability decide the choice: connected repeatable stages support consistent reruns. This costs the small team effort to set up and maintain the pipeline, but supports faster iteration once established.

### Consequences

* Pipeline definitions and stages need ownership.
* A failed stage can be isolated and rerun.
* Up-front automation work is required.

## Pros and Cons of the Options

### Orchestrated ML pipeline

* Good, because Reproducibility: repeatable connected stages
* Good, because Reliability: consistent run sequence
* Bad, because Team effort: pipeline setup and upkeep
* Sources: `s02_p09`, `s06_p07`, `s06_p13`

### Manual script-driven workflow

* Good, because Team effort: simple to start
* Bad, because Reliability: manual steps can vary
* Bad, because Fast iteration: repeated handoffs
* Sources: `s04_p02`, `s09_p08`, `s21_p07`
