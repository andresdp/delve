# How should model updates be protected?

* System: On-device visual inspection

## Context and Problem Statement

A weekly trained model is pushed into a production inspection system. A faulty update could reduce defect detection until replaced.

## Decision Drivers

* Production inspection
* Weekly model changes
* Small team

## Considered Options

* Replace model in place
* Versioned rollout with rollback

## Decision Outcome

Chosen option: "Versioned rollout with rollback".

Keeping model versions and a rollback path limits the impact of a problematic weekly update. This adds deployment logic and storage, but is a practical safeguard for production inspection.

### Consequences

* Devices need a way to retain or reacquire a known-good model.
* The team must define when to halt or reverse a rollout.

## Pros and Cons of the Options

### Replace model in place

* Good, because Simple deployment
* Good, because Low storage needs
* Bad, because Harder rollback
* Bad, because Update failure impact

### Versioned rollout with rollback

* Good, because Supports rollback
* Good, because Tracks deployed versions
* Bad, because Keeps multiple artifacts
* Bad, because Needs rollout logic
