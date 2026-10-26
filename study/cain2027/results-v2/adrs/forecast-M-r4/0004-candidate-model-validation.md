# Candidate model validation

* System: Retail demand forecasting

## Context and Problem Statement

New models need a quick path to production, but must not jeopardize the weekly forecast run. Evaluation should catch a quality regression before promotion.

## Decision Drivers

* Protect weekly run
* Fast model iteration
* Forecast quality

## Considered Options

* Threshold-based quality regression testing (`v:13.2`)
* Offline evaluation pipeline (`v:13.1`)

## Decision Outcome

Chosen option: "Threshold-based quality regression testing" (`v:13.2`).

Protecting the weekly run decides the choice: a candidate should fail promotion when it crosses a quality regression threshold. Thresholds need to be selected and maintained for the forecasting objective.

### Consequences

* Define and version acceptance thresholds.
* Failed candidates leave the production model unchanged.

## Pros and Cons of the Options

### Threshold-based quality regression testing

* Good, because Protect weekly run: blocks threshold regressions
* Good, because Fast iteration: automated promotion signal
* Bad, because Quality coverage: thresholds need calibration
* Sources: `s06_p02`, `s06_p08`

### Offline evaluation pipeline

* Good, because Forecast quality: tests against held-out data
* Bad, because Protect weekly run: does not itself define a regression threshold
* Sources: `s02_p05`
