# Artifact version control

*How much model lifecycle metadata should be governed?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly training creates successive model artifacts that must be distinguished when distributing updates and recovering from failures. The brief gives no requirement for broad experiment or dataset governance.

## Decision Drivers

* Repeated model versions
* Reproducible deployment
* Tight budget

## Considered Options

* Artifact version control (`v:20.1`)
* Comprehensive ML lifecycle traceability (`v:20.3`)

## Decision Outcome

Chosen option: "Artifact version control" (`v:20.1`).

Versioning each deployable model supports device updates and rollback while keeping governance effort proportionate to a small team. Sources including “Three Levels of ML Software” support artifact versioning; the checked combination was novel and returned no warnings or attesting sources.

### Consequences

* Assign each released model an immutable version.
* Retain enough metadata to identify the deployed version.

## Pros and Cons of the Options

### Artifact version control

* Good, because Tracks deployable models
* Good, because Supports reuse
* Bad, because Requires artifact storage
* Bad, because Limited lifecycle context
* Sources: `s12_p05`, `s19_p05`

### Comprehensive ML lifecycle traceability

* Good, because Links data, runs, and models
* Good, because Supports auditability
* Bad, because More metadata to manage
* Bad, because Higher setup effort
* Sources: `s08_p01`, `s22_p06`
