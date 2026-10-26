# What triggers retraining?

* System: On-device visual inspection

## Context and Problem Statement

The brief fixes retraining at a weekly cadence. A scheduled trigger maps directly to that requirement; monitoring can still inform later changes to the cadence.

## Decision Drivers

* Weekly cadence
* Small team

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Performance- or drift-based retraining trigger (`v:6.8`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

Choose the required weekly schedule. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” discuss recurring retraining; the checked design point also included this trigger, though it had no source attestation as a complete combination.

### Consequences

* Run training and evaluation on a weekly schedule.
* Monitor drift and quality to inform future cadence decisions.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Matches weekly cycle
* Good, because Predictable operations
* Bad, because May train without meaningful change
* Bad, because Does not react immediately to drift
* Sources: `s02_p08`, `s06_p07`, `s22_p08`

### Performance- or drift-based retraining trigger

* Good, because Responds to detected change
* Good, because Can avoid unnecessary runs
* Bad, because Needs monitoring thresholds
* Bad, because May miss changes without labels
* Sources: `s04_p05`, `s06_p02`, `s24_p07`
