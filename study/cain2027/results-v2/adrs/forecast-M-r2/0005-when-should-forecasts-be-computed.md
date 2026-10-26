# When should forecasts be computed?

* System: Retail demand forecasting

## Context and Problem Statement

The brief specifies weekly demand by store and product and gives no real-time serving requirement. Scheduled batch prediction fits the stated cadence and keeps the operating design focused on the weekly run.

## Decision Drivers

* Weekly-run reliability
* Team of three
* Fast model iteration

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

The weekly cadence and three-person team decide the choice: scheduled batch scoring aligns computation to the stated need without adding online serving operations. This gives up request-time freshness, which the brief does not require; sources include “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and Azure’s model management guidance.

### Consequences

* Publish a versioned forecast set after each scheduled run.
* Consumers use the latest completed forecast set.
* Set a schedule and recovery procedure for missed runs.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Team effort: matches weekly cadence
* Good, because Reliability: produces a forecast set per run
* Bad, because Freshness: predictions update on schedule
* Sources: `s01_p08`, `s02_p02`, `s02_p12`, `s19_p14`, `s25_p06`

### Online computation serving

* Good, because Freshness: uses current request context
* Bad, because Team effort: adds online serving operations
* Bad, because Weekly-run reliability: more runtime dependencies
* Sources: `s02_p02`, `s04_p10`, `s12_p02`, `s19_p08`
