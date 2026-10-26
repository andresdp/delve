# How should forecasts be reproducible for past weeks?

* System: Retail demand forecasting

## Context and Problem Statement

Priority order: reproduce forecasts for any past week; release model ideas quickly without disrupting the weekly run; keep the end-to-end pipeline manageable for three data scientists. Reproducing a forecast requires retaining the inputs and model artifacts used at that time.

## Decision Drivers

* Reproducibility: any past week
* Safe weekly run
* Small-team ownership

## Considered Options

* Versioned inputs and model artifacts
* Recompute from current data and code

## Decision Outcome

Chosen option: "Versioned inputs and model artifacts".

Reproducibility decides the choice: retaining the inputs and model artifact makes past runs recoverable. This costs storage and requires version tracking.

### Consequences

* Record input and model versions for each weekly run.
* Retain artifacts for the required historical period.
* Past forecasts can be audited or regenerated.

## Pros and Cons of the Options

### Versioned inputs and model artifacts

* Good, because Reproducibility: recover exact inputs and model
* Good, because Small-team ownership: simple audit trail
* Bad, because Cost: retain historical artifacts

### Recompute from current data and code

* Good, because Small-team ownership: fewer stored artifacts
* Bad, because Reproducibility: past inputs may change
* Bad, because Safe weekly run: results may drift
