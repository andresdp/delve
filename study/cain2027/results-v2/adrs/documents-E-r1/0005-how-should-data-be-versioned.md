# How should data be versioned?

* System: Large-scale document classification

## Context and Problem Statement

Classification quality must be monitored over time, and data versioning can help identify which data informed a model or result. The design space offers a dedicated data version repository (d:11).

## Decision Drivers

* Quality drift visibility
* Reproducibility

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Drift investigation and reproducibility decide the choice; explicit data versions add operating cost but help trace model inputs.

### Consequences

* Retain links between model releases and data versions.
* Budget storage for versioned datasets.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: track data versions explicitly
* Bad, because Cost: operate versioning infrastructure
* Sources: `d:11`, `v:11.1`

### No data versioning

* Bad, because Reproducibility: harder to trace training data
* Sources: `d:11`, `v:11.3`
