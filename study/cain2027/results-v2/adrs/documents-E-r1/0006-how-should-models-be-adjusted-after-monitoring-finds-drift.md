# How should models be adjusted after monitoring finds drift?

* System: Large-scale document classification

## Context and Problem Statement

Operators need drift visibility, but the brief does not authorize automatic retraining or deployment. The design space offers manual and automated adjustment (d:24).

## Decision Drivers

* Quality drift visibility
* Operational control

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Operational control decides the choice because the brief asks operators to see drift but does not require automated correction; slower response is the trade-off.

### Consequences

* Define an operator review and retraining process.
* Drift alerts do not change production models by themselves.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Quality: operators review drift before changes
* Bad, because Response time: adjustment waits for human action
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Response time: trigger changes without manual delay
* Bad, because Operational control: automated changes need safeguards
* Sources: `d:24`, `v:24.2`
