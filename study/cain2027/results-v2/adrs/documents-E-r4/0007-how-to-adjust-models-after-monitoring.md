# How to adjust models after monitoring

* System: Large-scale document classification

## Context and Problem Statement

Monitoring can reveal drift, but the brief does not authorize or describe automatic model updates; classification quality is operationally important.

## Decision Drivers

* Detect quality drift

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Quality control decides: the brief requires drift visibility but gives no policy for safe automatic adaptation. We accept slower recovery so operators can review model changes.

### Consequences

* Operators must review alerts and adjust models.
* Retraining and promotion procedures remain to be defined.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Quality control: humans review changes
* Bad, because Recovery time: requires operator action
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Recovery time: can trigger adjustments automatically
* Bad, because Quality control: changes occur without manual review
* Sources: `d:24`, `v:24.2`
