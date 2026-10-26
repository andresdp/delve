# How should monitoring results change models?

* System: Retail demand forecasting

## Context and Problem Statement

The brief prioritizes quick model iteration but also requires the weekly run not to break. Human review can gate model changes based on observed results.

## Decision Drivers

* Fast iteration
* Run stability
* Small team

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Manual review keeps a person in control of model changes while the team establishes reliable monitoring and evaluation (d:24, v:24.1).

### Consequences

* The team reviews monitoring outcomes.
* Model updates may wait for review.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Human approval gate
* Good, because Controlled changes
* Bad, because Slower response
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Faster adaptation
* Bad, because More failure modes
* Sources: `d:24`, `v:24.2`
