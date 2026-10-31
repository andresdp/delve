# Gate model promotion on offline evaluation

* System: On-device visual inspection

## Context and Problem Statement

Each weekly candidate should be assessed before it replaces the model on production devices.

## Decision Drivers

* Weekly candidates
* Regression control

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Threshold-based quality regression testing (`v:13.2`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Offline evaluation fits the weekly batch cycle and checks candidates against held-out labelled examples before release. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “MLOps: Continuous delivery and automation pipelines in machine learning” document pre-deployment evaluation.

### Consequences

* Maintain a held-out set representative of production defects.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Tests held-out data
* Good, because Pre-promotion check
* Bad, because Requires labelled evaluation data
* Sources: `s02_p09`, `s04_p15`

### Threshold-based quality regression testing

* Good, because Detects quality drops
* Good, because Supports promotion gates
* Bad, because Thresholds need maintenance
* Sources: `s06_p08`, `s22_p09`
