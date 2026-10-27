# Data preservation and provenance

* System: Retail demand forecasting

## Context and Problem Statement

A past forecast can only be reproduced if the historical inputs and their transformation history remain available. Preserving provenance is therefore part of the replay capability.

## Decision Drivers

* Historical replay
* Data traceability
* Model comparison

## Considered Options

* Traceable and preserved data (`v:42.1`)
* Cataloged data (`v:42.2`)

## Decision Outcome

Chosen option: "Traceable and preserved data" (`v:42.1`).

Immutable, traceable source data supports reconstructing inputs for any historical week, directly serving the brief’s reproducibility requirement. “Architecting a Machine Learning Pipeline” and “Architecting a Machine Learning System for Risk” support preserving original data and provenance. The checked point has no warnings but is unattested.

### Consequences

* Set retention rules for historical source data.
* Link each forecast run to its input snapshot.

## Pros and Cons of the Options

### Traceable and preserved data

* Good, because Retains original inputs
* Good, because Tracks processing history
* Bad, because Retention cost
* Bad, because Requires data lifecycle policy
* Sources: `s02_p04`, `s02_p05`, `s02_p06`, `s10_p08`, `s12_p07`, `s29_p08`

### Cataloged data

* Good, because Records dataset metadata
* Good, because Improves discoverability
* Bad, because Does not ensure preservation
* Bad, because May not retain provenance
