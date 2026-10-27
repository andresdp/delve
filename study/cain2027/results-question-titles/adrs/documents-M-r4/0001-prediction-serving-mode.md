# Prediction serving mode

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, with volume that varies through the year. The brief does not require immediate predictions for each incoming document.

## Decision Drivers

* high daily volume
* seasonal demand
* shared results

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Batch scoring fits the stated scale and shared consumption model; no per-document response-time requirement is given. Sources including “Architecting a Machine Learning Pipeline” and “System Architectures for Personalization and Recommendation” describe scheduled scoring.

### Consequences

* Consumers read results from shared storage or analytics systems.
* Results reflect the most recent completed scoring run.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because scores large volumes
* Good, because writes results for consumers
* Bad, because results wait for the batch
* Sources: `s02_p02`, `s12_p02`, `s15_p04`

### Queue-fronted online serving cluster

* Good, because handles online requests
* Good, because supports load balancing
* Bad, because keeps serving capacity available
* Sources: `s02_p11`, `s12_p07`
