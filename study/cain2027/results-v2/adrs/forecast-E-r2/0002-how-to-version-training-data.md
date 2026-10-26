# How to version training data?

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a forecast for a past week requires knowing which data was used to train and generate it. The design space compares repository-based versioning with code repository versioning and no versioning (d:11).

## Decision Drivers

* Reproduce any past week
* Small team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducing any past week decides the choice: use a dedicated data version repository, accepting the added tool overhead (d:11, v:11.1).

### Consequences

* Record the data version used for each forecast run.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: dedicated data version history
* Bad, because Small team: another tool to operate

### Data versioning in code repository

* Good, because Reproducibility: version data alongside code
* Bad, because Small team: repository may not suit large datasets

### No data versioning

* Bad, because Reproducibility: past inputs are hard to recover
