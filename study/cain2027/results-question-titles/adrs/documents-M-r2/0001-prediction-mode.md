# Prediction mode

* System: Large-scale document classification

## Context and Problem Statement

The classifier processes millions of documents daily, with seasonal volume swings and multiple downstream teams. The brief does not require request-time results.

## Decision Drivers

* High daily volume
* Seasonal demand
* Shared results

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Scheduled batch scoring fits the stated large daily volume and shared consumption. Sources including “How to power up your product by machine learning with python microservice, pt. 1” describe batch deployment; the checked design point was unattested, so this is a reasoned choice rather than a documented combination.

### Consequences

* Consumers read persisted classification results.
* Processing capacity must accommodate seasonal peaks.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because High-throughput scoring
* Good, because Results persist for consumers
* Bad, because Results arrive on a schedule
* Sources: `s01_p08`

### Online computation serving

* Good, because Fresh per-request results
* Good, because Supports interactive use
* Bad, because Serves requests individually
* Sources: `s02_p02`, `s02_p13`
