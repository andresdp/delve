# Review drift before adjusting the model

* System: Large-scale document classification

## Context and Problem Statement

The brief requires drift visibility but does not authorize automatic model changes. Manual and automated adjustment are alternatives in the design space (d:24).

## Decision Drivers

* Quality drift visibility
* No retraining policy specified

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Manual review is the conservative choice because the brief asks operators to observe drift but gives no criteria or authority for automatic adaptation. The design space relates monitoring choices to adjustment choices (d:22 to d:24).

### Consequences

* Operators review drift signals and decide actions.
* Response time depends on the review process.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Human review before changes
* Good, because Explicit redeployment control
* Bad, because Slower response to drift
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Can respond quickly
* Good, because Reduces manual intervention
* Bad, because Needs safe adjustment rules
* Sources: `d:24`, `v:24.2`
