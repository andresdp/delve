# How should model releases be checked and reversed?

* System: On-device visual inspection

## Context and Problem Statement

Weekly model updates can change inspection outcomes across production devices. A release process needs a way to limit the impact of a poor model.

## Decision Drivers

* Weekly model changes
* Production inspection
* Small team

## Considered Options

* Stage rollout with a prior-version fallback
* Replace the model fleet-wide immediately

## Decision Outcome

Chosen option: "Stage rollout with a prior-version fallback".

Staged deployment and a retained previous version give the team a practical way to contain and reverse regressions.

### Consequences

* Devices need to retain a known prior model.
* Rollout progress and failures need tracking.

## Pros and Cons of the Options

### Stage rollout with a prior-version fallback

* Good, because Limits rollout impact
* Good, because Enables rollback
* Bad, because Needs release coordination
* Bad, because Fallback uses older model

### Replace the model fleet-wide immediately

* Good, because Simple release flow
* Good, because Fast fleet coverage
* Bad, because Broad failure impact
* Bad, because Rollback is harder
