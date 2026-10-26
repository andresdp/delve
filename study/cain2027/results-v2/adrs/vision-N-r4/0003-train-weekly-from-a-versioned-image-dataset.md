# Train weekly from a versioned image dataset

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images drive weekly retraining, so each model should be traceable to the data and labels used. The brief does not specify a data platform.

## Decision Drivers

* Weekly model freshness
* Reproducibility
* Low infrastructure cost

## Considered Options

* Versioned dataset snapshots
* Train from a mutable image store

## Decision Outcome

Chosen option: "Versioned dataset snapshots".

Reproducibility decides the choice: each weekly run can be tied to a fixed set of images and labels. This gives up the lower setup cost of a mutable store.

### Consequences

* Retain dataset and label versions alongside model records.
* Storage needs grow as snapshots accumulate.

## Pros and Cons of the Options

### Versioned dataset snapshots

* Good, because Reproducibility: records training inputs
* Good, because Weekly model freshness: supports repeatable retraining
* Bad, because Infrastructure cost: requires dataset storage and organization

### Train from a mutable image store

* Good, because Infrastructure cost: minimal data-management setup
* Bad, because Reproducibility: contents can change between runs
