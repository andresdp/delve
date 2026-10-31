# Use scheduled batch scoring for document classification

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents daily, with seasonal volume swings and no stated per-document latency target.

## Decision Drivers

* Millions of documents daily
* Seasonal volume variation
* Several consuming teams

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

The brief establishes large, variable volume but no immediate response requirement. Scheduled scoring fits those needs; the checked rival point used online serving, but neither combination was attested by the workspace sources.

### Consequences

* Teams consume persisted classification results after each run.
* Run cadence and completion time become operational concerns.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Writes results for downstream use
* Good, because Supports high-volume scoring
* Bad, because Results arrive on a schedule
* Sources: `s02_p02`, `s02_p12`, `s02_p13`, `s15_p04`, `s15_p05`

### Queue-fronted online serving cluster

* Good, because Handles variable request load
* Good, because Supports low-latency responses
* Bad, because Adds always-on serving complexity
* Sources: `s02_p11`, `s02_p13`, `s19_p15`
