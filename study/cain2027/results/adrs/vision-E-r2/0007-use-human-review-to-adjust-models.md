# Use human review to adjust models

* System: On-device visual inspection

## Context and Problem Statement

A model update can affect production inspection, and the small team needs a controlled release process.

## Decision Drivers

* Defect quality
* Weekly retraining
* Small team

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Human review of monitoring results provides a controlled basis for approving weekly model changes (d:24, v:24.1).

### Consequences

* Review candidate models before deployment.
* Updates may wait for the next review.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Human release control
* Good, because Fits weekly review
* Bad, because Requires review effort
* Bad, because Slower response
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Fast reaction
* Good, because Less manual intervention
* Bad, because Needs safe automation
* Bad, because Harder to diagnose
* Sources: `d:24`, `v:24.2`
