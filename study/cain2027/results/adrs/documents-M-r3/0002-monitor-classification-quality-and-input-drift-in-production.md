# Monitor classification quality and input drift in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility when classification quality drifts, while input changes can signal that model behavior needs investigation.

## Decision Drivers

* Detect quality drift
* Observe changing inputs
* Operational visibility

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Use input and feature drift as the primary early signal, and assess prediction quality when labels become available. These are complementary practices in the design space, whose exclusivity is zero; the checked point warns that its one-value-per-dimension rule does not encode this bundle.

### Consequences

* Quality evaluation follows label availability.
* Drift alerts require operator interpretation.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Surfaces changing inputs
* Good, because Can reveal drift early
* Bad, because Drift does not prove quality loss
* Sources: `s04_p03`, `s04_p05`, `s06_p02`, `s06_p08`, `s23_p03`

### Real-time prediction-quality monitoring

* Good, because Tracks model behavior
* Good, because Measures quality when labels arrive
* Bad, because Depends on available labels
* Sources: `s04_p02`, `s04_p12`, `s06_p06`, `s06_p13`, `s23_p04`
