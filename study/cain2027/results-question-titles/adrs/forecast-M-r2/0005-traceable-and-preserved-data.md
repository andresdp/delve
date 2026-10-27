# Traceable and preserved data

*How should source data be preserved?*

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a past forecast depends on recovering the data state used for that week. The design space describes preserving source data and its provenance as one approach.

## Decision Drivers

* Past-week reproducibility
* Data traceability
* Run reconstruction

## Considered Options

* Traceable and preserved data (`v:42.1`)
* Cataloged data (`v:42.2`)

## Decision Outcome

Chosen option: "Traceable and preserved data" (`v:42.1`).

Preserving the original data with provenance makes historical inputs more recoverable than cataloging metadata alone. Architecting a Machine Learning Pipeline and Architecting a Machine Learning System for Risk describe provenance and preservation practices.

### Consequences

* Define retention for source data and derived inputs.
* The checked design point leaves data ingestion undecided.

## Pros and Cons of the Options

### Traceable and preserved data

* Good, because Preserves original data
* Good, because Records provenance
* Bad, because Requires retention capacity
* Sources: `s02_p04`, `s02_p05`, `s02_p06`, `s10_p08`

### Cataloged data

* Good, because Records metadata and versions
* Good, because Improves data discovery
* Bad, because Catalog alone may not preserve past contents
* Sources: `s04_p05`, `s06_p09`, `s20_p08`
