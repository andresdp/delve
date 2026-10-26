# Test trained model quality before release

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces new candidates for deployment, so a quality gate is needed before replacing the current model. The design space lists trained-model quality testing (d:26).

## Decision Drivers

* Weekly retraining
* Offline inference
* Small team and tight budget

## Considered Options

* Testing trained model quality (`v:26.9`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Offline inference decides the choice: once a poor model reaches a disconnected device, recovery may be delayed. Quality testing adds evaluation work before deployment.

### Consequences

* Set a quality acceptance criterion for each candidate.
* Keep evaluation data representative of production defects.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Weekly retraining: checks each candidate
* Bad, because Small team: requires evaluation data and review effort
* Sources: `d:26`, `v:26.9`

### No testing

* Good, because Cost: no test setup
* Bad, because Offline inference: poor model may persist until next rollout
* Sources: `d:26`, `v:26.14`
