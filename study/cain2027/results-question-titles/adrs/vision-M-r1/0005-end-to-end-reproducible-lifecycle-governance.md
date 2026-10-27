# End-to-end reproducible lifecycle governance

*How should models and training runs be tracked?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces successive model versions that need to be identified and made reproducible for device rollout and recovery.

## Decision Drivers

* weekly versions
* reproducibility
* rollback

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Linking datasets, training snapshots, artifacts, and deployment health makes weekly releases traceable and supports recovery. The checked combination returned no warnings but had no adopting sources.

### Consequences

* Record the data and configuration behind each model.
* Keep device version and deployment status visible.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because tracks data and runs
* Good, because supports audit and recovery
* Bad, because metadata overhead
* Bad, because process setup
* Sources: `s21_p03`, `s21_p05`, `s21_p09`, `s25_p01`

### Artifact version control

* Good, because tracks deployable models
* Good, because lower process scope
* Bad, because limited training context
* Bad, because weaker lineage
