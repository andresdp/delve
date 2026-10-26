# Scheduled batch prediction deployment

*How should document classifications be computed and delivered?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive each day, with volume varying substantially by season. The brief gives no per-document latency target, so scheduled scoring can meet the stated scale without assuming real-time delivery.

## Decision Drivers

* Daily volume
* Seasonal demand swings
* Unspecified latency target

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Daily volume and absent latency requirements favor scheduled batch scoring, as described in “Architecting a Machine Learning Pipeline” and “Three Levels of ML Software.” This gives up immediate per-document results; the point check returned no warnings, though its combination was unattested.

### Consequences

* Classification results are available after each scoring run.
* Run frequency must balance freshness and compute cost.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Daily volume: scores large workloads in batches
* Good, because Seasonal demand: schedule work around demand
* Bad, because Freshness: results wait for the next run
* Sources: `s02_p02`, `s02_p12`, `s02_p13`, `s12_p02`, `s19_p14`, `s19_p16`, `s25_p06`

### Queue-fronted online serving cluster

* Good, because Daily volume: distributes scoring across predictors
* Bad, because Cost: capacity must support online demand
* Bad, because Unspecified latency: adds needless serving complexity
* Sources: `s02_p11`, `s02_p13`, `s12_p07`, `s19_p15`
