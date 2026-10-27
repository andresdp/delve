# Versioned, staged model rollout

*How should classifier updates be introduced?*

* System: Large-scale document classification

## Context and Problem Statement

An LLM-based classifier produces results used by several teams, and operators need to monitor quality drift. Changes to the classifier can therefore affect both quality and downstream use.

## Decision Drivers

* LLM classification
* Quality drift
* Several consumers

## Considered Options

* Versioned, staged model rollout
* Replace the active model directly

## Decision Outcome

Chosen option: "Versioned, staged model rollout".

Staging and versioning make quality changes observable and limit the impact of a classifier update on consuming teams.

### Consequences

* Results need to identify the classifier version.
* Rollouts require comparison and promotion steps.

## Pros and Cons of the Options

### Versioned, staged model rollout

* Good, because Limits rollout exposure
* Good, because Supports comparison
* Bad, because Requires version tracking
* Bad, because Adds rollout steps

### Replace the active model directly

* Good, because Simple deployment path
* Good, because No parallel capacity
* Bad, because Broad immediate impact
* Bad, because Harder to compare
