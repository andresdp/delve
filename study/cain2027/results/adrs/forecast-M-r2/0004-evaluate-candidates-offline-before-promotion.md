# Evaluate candidates offline before promotion

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a consistent check against known outcomes before replacing the production forecast.

## Decision Drivers

* Prevent regressions
* Compare candidates
* Safe promotion

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)
* Threshold-based quality regression testing (`v:13.2`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Offline candidate evaluation gives the team a pre-production check against known outcomes. Threshold-based regression checks can complement this choice, but the brief does not specify forecast metrics or acceptable thresholds; practitioner sources describe both offline evaluation and threshold-based regression checks.

### Consequences

* Maintain an evaluation dataset representative of past weeks.
* Choose forecast metrics and promotion thresholds.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Tests candidates before deployment
* Good, because Uses held-out data
* Bad, because Depends on representative test data
* Bad, because Does not define acceptance thresholds
* Sources: `s02_p09`, `s04_p15`, `s06_p08`

### Metric-driven candidate model evaluation

* Good, because Compares multiple candidates
* Good, because Uses selected metrics
* Bad, because Metric choice needs justification
* Bad, because Does not alone gate release
* Sources: `s02_p09`, `s09_p04`, `s22_p06`

### Threshold-based quality regression testing

* Good, because Flags quality drops
* Good, because Can gate promotion
* Bad, because Thresholds need calibration
* Bad, because Does not specify candidate evaluation alone
* Sources: `s06_p02`, `s06_p08`, `s22_p09`
