# Data preservation for forecast replay

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a forecast from a past week requires retaining its input data and provenance. The brief does not state retention or privacy constraints.

## Decision Drivers

* Past-week reproducibility
* Input provenance
* Auditability

## Considered Options

* Traceable and preserved data (`v:42.1`)
* Cataloged data (`v:42.2`)

## Decision Outcome

Chosen option: "Traceable and preserved data" (`v:42.1`).

Keeping inputs recoverable with their provenance supports replaying forecasts from past weeks. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Architecting a Machine Learning System for Risk” support preservation and traceability.

### Consequences

* Retain source snapshots or equivalent immutable inputs.
* Record processing provenance for each forecast run.
* Set retention and access policies.

## Pros and Cons of the Options

### Traceable and preserved data

* Good, because Retains original inputs
* Good, because Tracks provenance
* Bad, because Storage and retention cost
* Sources: `s02_p04`, `s02_p05`, `s02_p06`, `s10_p08`, `s12_p07`, `s29_p08`

### Cataloged data

* Good, because Documents data versions
* Good, because Improves discoverability
* Bad, because Preservation not explicit
