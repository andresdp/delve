# Batch-based learning

*When and how to train?*

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasting suggests a recurring model build, while reproducibility favors repeatable training runs. The design space includes batch, incremental, and hybrid learning (d:19).

## Decision Drivers

* Reproduce any past week
* Protect weekly run
* Ship model ideas quickly

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Reproducibility decides the choice: batch training makes runs repeatable, at the cost of waiting for the next scheduled run to try a model change (d:19, v:19.1).

### Consequences

* Keep training separate from forecast generation where practical.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Reproducibility: repeatable offline runs
* Good, because Protect weekly run: scheduled training
* Bad, because Ship model ideas quickly: changes await a run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Ship model ideas quickly: update continuously
* Bad, because Reproducibility: harder to reconstruct model state
* Bad, because Protect weekly run: continuous updates add operational risk

### Hybrid batch-based and incremental learning

* Good, because Ship model ideas quickly: some updates are incremental
* Bad, because Small team: greater operational complexity
