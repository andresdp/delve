# Manual model adjustment

*How should the model be adjusted when monitoring finds drift?*

* System: Large-scale document classification

## Context and Problem Statement

Drift visibility implies a response when quality degrades. The design space offers manual or automated model adjustment (d:24).

## Decision Drivers

* Drift visibility

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Drift visibility decides the choice: human review provides a controlled response when quality changes. This gives up the faster response automated adjustment may offer.

### Consequences

* Operators need a review and redeployment process.
* Drift alerts require timely human attention.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Drift visibility: people review evidence before changing models
* Bad, because Drift visibility: response may be delayed
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Drift visibility: automated action can follow detected changes
* Bad, because Drift visibility: adjustment may occur without human review
* Sources: `d:24`, `v:24.2`
