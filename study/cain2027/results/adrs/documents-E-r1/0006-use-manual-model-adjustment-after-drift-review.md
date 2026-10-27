# Use manual model adjustment after drift review

* System: Large-scale document classification

## Context and Problem Statement

Monitoring may reveal that classification quality has changed, so the system needs a response path. The brief asks for visibility but does not authorize automatic model changes.

## Decision Drivers

* Respond to drift
* Operator oversight

## Considered Options

* Manual model adjustment (`v:24.1`)
* Automated model adjustment (`v:24.2`)

## Decision Outcome

Chosen option: "Manual model adjustment" (`v:24.1`).

Manual review keeps model changes under operator control, and the brief requires visibility rather than automated correction. The checked point has no warnings; its rival also has no warnings, leaving the desired level of automation unspecified.

### Consequences

* Operators review drift alerts and decide on remediation.
* Model updates require a deployment process.

## Pros and Cons of the Options

### Manual model adjustment

* Good, because Human review before changes
* Good, because Controlled redeployment
* Bad, because Slower response
* Sources: `d:24`, `v:24.1`

### Automated model adjustment

* Good, because Can respond quickly
* Good, because Reduces manual operation
* Bad, because May act on noisy signals
* Sources: `d:24`, `v:24.2`
