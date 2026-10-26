# How should input drift be detected?

* System: Large-scale document classification

## Context and Problem Statement

The brief calls out quality drift but does not specify whether it comes from changing document inputs or changing model behavior. Input monitoring provides an early signal alongside labeled quality measurements.

## Decision Drivers

* Drift visibility
* Changing document mix
* Operational diagnosis

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Software-metrics-only monitoring (`v:6.10`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Combine input-drift checks with the quality monitoring decision: they address complementary signals, and monitoring alternatives in this dimension are not exclusive. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Continuous delivery and automation pipelines in machine learning” describe monitoring input, schema, and statistical changes.

### Consequences

* Compare incoming document characteristics with a baseline.
* Investigate drift before treating it as confirmed quality loss.
* Coordinate drift alerts with the quality dashboard.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Detects input changes
* Good, because Can signal before labels
* Bad, because Drift is not quality loss
* Bad, because Requires reference distributions
* Sources: `s04_p03`, `s06_p02`, `s23_p03`

### Software-metrics-only monitoring

* Good, because Tracks service health
* Bad, because Misses ML input shifts
* Bad, because Misses prediction quality
