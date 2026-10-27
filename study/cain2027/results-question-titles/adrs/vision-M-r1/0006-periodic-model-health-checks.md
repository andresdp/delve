# Periodic model health checks

*How should deployed models be monitored and adapted?*

* System: On-device visual inspection

## Context and Problem Statement

Production images and operating conditions may change, and model health must inform subsequent weekly retraining.

## Decision Drivers

* defect detection quality
* weekly retraining
* small team

## Considered Options

* Periodic model health checks (`v:6.18`)
* Automated retraining pipeline (`v:6.5`)

## Decision Outcome

Chosen option: "Periodic model health checks" (`v:6.18`).

The weekly retraining cadence suits scheduled health review, and periodic checks keep operational burden bounded for a small team. The evidence identifies automated retraining as an option, but the brief only requires weekly retraining, not autonomous promotion.

### Consequences

* Review model and service health at least weekly.
* Gate each candidate on evaluation before release.

## Pros and Cons of the Options

### Periodic model health checks

* Good, because fits scheduled review
* Good, because lower continuous operations load
* Bad, because issues may wait until review
* Bad, because requires health signals
* Sources: `s06_p02`, `s20_p03`, `s23_p08`

### Automated retraining pipeline

* Good, because automates recurring retraining
* Good, because uses new labeled data
* Bad, because needs quality gates
* Bad, because automated release risk
* Sources: `s04_p01`, `s06_p02`, `s06_p06`
