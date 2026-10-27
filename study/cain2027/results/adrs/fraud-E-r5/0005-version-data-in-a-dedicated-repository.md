# Version data in a dedicated repository

* System: Card-fraud scoring service

## Context and Problem Statement

Reconstructing a score requires identifying the features and data state used to produce it. The design space includes a dedicated data version repository as one approach.

## Decision Drivers

* Audit reconstruction
* Data provenance

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository offers explicit support for data versioning, which helps identify the data used in an audited score. The design point reported no warnings; the batch rival used no data versioning.

### Consequences

* Maintain links between score records and data versions.
* Choose retention and version granularity.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data version support
* Bad, because Additional repository to operate
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versions with code
* Bad, because Fit for data unspecified
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Weak data provenance
* Sources: `d:11`, `v:11.3`
