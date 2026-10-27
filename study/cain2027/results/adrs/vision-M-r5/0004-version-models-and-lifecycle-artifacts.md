# Version models and lifecycle artifacts

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining and device distribution create successive model packages; the team needs to identify which model and training inputs produced each release.

## Decision Drivers

* Repeatable releases
* Release traceability
* Small team

## Considered Options

* Artifact version control (`v:20.1`)
* Comprehensive ML lifecycle traceability (`v:20.3`)

## Decision Outcome

Chosen option: "Artifact version control" (`v:20.1`).

Versioning the model artifacts establishes the basic identity needed to track weekly device releases without assuming a larger lifecycle platform. Comprehensive traceability offers broader lineage, but the brief’s small team and tight budget favor beginning with artifact versions.

### Consequences

* Tag every device package with its model version.
* Retain the training inputs and run details needed to reproduce releases.

## Pros and Cons of the Options

### Artifact version control

* Good, because Versions model assets
* Good, because Supports reproducible deployment
* Bad, because Requires artifact management
* Sources: `s12_p05`, `s19_p05`

### Comprehensive ML lifecycle traceability

* Good, because Links runs, data, and models
* Good, because Supports audit trail
* Bad, because More metadata upkeep
* Bad, because More process overhead
* Sources: `s08_p01`, `s22_p06`, `s22_p13`
