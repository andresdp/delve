# Real-time prediction-quality monitoring

*How should classification quality be monitored?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility into quality drift after deployment. Classification labels may arrive after predictions, so quality measurement depends on label availability.

## Decision Drivers

* Quality drift visibility
* Delayed labels
* Operator awareness

## Considered Options

* Real-time prediction-quality monitoring (`v:6.1`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Real-time prediction-quality monitoring" (`v:6.1`).

The brief explicitly requires operators to see quality drift, so active quality monitoring is necessary. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Machine Learning Monitoring: What It Is, and What We Are Missing” describe measuring deployed prediction quality.

### Consequences

* Retain predictions and eventual labels for comparison.
* Report quality by claim type and time window.
* Quality alerts may lag until labels arrive.

## Pros and Cons of the Options

### Real-time prediction-quality monitoring

* Good, because Surfaces quality changes
* Good, because Tracks live model behavior
* Bad, because Needs labels for measurement
* Bad, because Requires monitoring coverage
* Sources: `s06_p06`, `s23_p03`, `s24_p05`

### Passive production operation

* Good, because Minimal monitoring setup
* Bad, because No active quality visibility
* Bad, because Drift may go unnoticed
