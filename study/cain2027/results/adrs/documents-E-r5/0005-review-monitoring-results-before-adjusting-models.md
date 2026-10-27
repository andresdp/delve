# Review monitoring results before adjusting models

* System: Large-scale document classification

## Context and Problem Statement

Monitoring can reveal quality changes, but the brief does not authorize automatic retraining or adjustment.

## Decision Drivers

* Quality drift visibility
* Controlled model changes

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Manual adjustment leaves model changes under operator control because the brief asks for drift visibility but gives no criteria for automatic intervention; this was the checked choice (d:24, v:24.1).

### Consequences

* Operators must review alerts and decide on changes.
* Model updates may take longer.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Human review of changes
* Good, because Explicit redeployment
* Bad, because Slower response
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Can react automatically
* Bad, because Change policy unspecified
* Sources: `d:24`, `v:24.2`
