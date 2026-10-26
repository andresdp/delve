# How to version training data?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need reproducible lineage from a deployed model to its training inputs. The design space presents a data version repository and no data versioning as options (d:11).

## Decision Drivers

* audit lineage
* reproducibility

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Explicitly versioned training data helps link each deployed model to its inputs, complementing the per-score model and feature record required by the brief (d:11, d:22).

### Consequences

* Record training data version in model metadata.
* Retain datasets or references for the required audit period.

## Pros and Cons of the Options

### Data version repository

* Good, because Explicit data versions
* Good, because Supports reproducibility
* Bad, because Repository operations
* Bad, because Storage overhead
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because Less infrastructure
* Good, because Fewer workflows
* Bad, because Weak lineage
* Bad, because Harder reproduction
* Sources: `d:11`, `v:11.3`
