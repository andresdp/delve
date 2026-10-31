# Retrain on a weekly schedule

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained every week from newly labelled images. The design space also describes retraining triggered by detected performance or data drift.

## Decision Drivers

* Weekly retraining
* New labelled images

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Performance- or drift-based retraining trigger (`v:6.8`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

A weekly schedule directly matches the brief. “MLOps: Continuous delivery and automation pipelines in machine learning” documents scheduled retraining; the rival point used drift-triggered retraining, which is not specified as the brief’s trigger.

### Consequences

* Run the training workflow weekly against available labelled images.
* Define handling for missing or late labels.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Matches weekly cadence
* Good, because Predictable workflow
* Bad, because May miss changes between runs
* Sources: `s02_p08`, `s06_p07`, `s06_p11`, `s20_p06`, `s20_p12`, `s22_p08`, `s24_p07`

### Performance- or drift-based retraining trigger

* Good, because Responds to degradation
* Good, because Can target needed updates
* Bad, because Needs monitoring signals
