# Production monitoring and retraining feedback

* System: On-device visual inspection

## Context and Problem Statement

The system receives newly labelled images and retrains weekly, but cameras may be offline. Monitoring should reveal input changes and inform model maintenance without relying on a continuous connection.

## Decision Drivers

* Reliable inference
* Weekly retraining
* Small-team operations

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Reliable inference decides the choice: drift monitoring can flag changed inputs for investigation, with setup and review effort as the trade-off. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” support monitoring input and feature changes. The design point combines drift monitoring with the weekly schedule and automated retraining; the workspace records no sources adopting that full combination.

### Consequences

* Monitoring results need to be collected when devices reconnect.
* Drift alerts require review and do not by themselves establish prediction quality.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Reliable inference: surfaces changing inputs
* Bad, because Small-team operations: requires monitoring setup
* Sources: `s06_p08`, `s22_p11`

### Passive production operation

* Good, because Small-team operations: little monitoring upkeep
* Bad, because Reliable inference: failures may go unnoticed
* Sources: `s23_p13`
