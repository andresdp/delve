# Evaluate candidates offline before promotion

* System: On-device visual inspection

## Context and Problem Statement

New weekly training runs produce candidates that must be checked before their model package reaches production devices.

## Decision Drivers

* Safe updates
* Candidate quality
* Limited operations capacity

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)
* Previously-built-model diff testing (`v:13.3`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

An offline pipeline checks candidates against held-out data and true labels before selection, fitting a controlled weekly update flow. This design point has no attesting sources and warns that workflow coordination must also be decided; its combination is therefore an architectural choice for this brief, not a directly attested pattern.

### Consequences

* Keep evaluation data separate from training inputs.
* Specify acceptance thresholds before device rollout.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Tests held-out data
* Good, because Supports pre-release selection
* Bad, because Needs representative evaluation data
* Sources: `s02_p09`, `s06_p08`, `s22_p08`

### Metric-driven candidate model evaluation

* Good, because Compares candidates
* Good, because Makes selection measurable
* Bad, because Metric choice requires care
* Bad, because Does not specify deployment checks
* Sources: `s02_p09`, `s09_p07`, `s22_p06`

### Previously-built-model diff testing

* Good, because Highlights output changes
* Bad, because Difficult to maintain
* Bad, because Mixed evidence
* Sources: `s06_p08`
