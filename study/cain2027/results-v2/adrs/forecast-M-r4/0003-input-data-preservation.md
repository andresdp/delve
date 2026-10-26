# Input data preservation

* System: Retail demand forecasting

## Context and Problem Statement

Past forecasts cannot be reconstructed if historical inputs or their provenance are lost. Preserving original data supports replay and comparison.

## Decision Drivers

* Past-week reproducibility
* Fast investigation

## Considered Options

* Traceable and preserved data (`v:42.1`)
* Cataloged data (`v:42.2`)

## Decision Outcome

Chosen option: "Traceable and preserved data" (`v:42.1`).

Past-week reproducibility decides the choice: retaining provenance and original inputs enables recovery of the data used for a forecast. This adds storage and retention work.

### Consequences

* Historical inputs need retention and access controls.
* Ingestion must record provenance.

## Pros and Cons of the Options

### Traceable and preserved data

* Good, because Reproducibility: provenance and original data retained
* Bad, because Storage cost: historical data retained
* Sources: `s02_p04`, `s02_p05`, `s10_p08`

### Cataloged data

* Good, because Fast investigation: profiles and versions discoverable
* Bad, because Reproducibility: catalog alone may not preserve original inputs
* Sources: `s02_p07`
