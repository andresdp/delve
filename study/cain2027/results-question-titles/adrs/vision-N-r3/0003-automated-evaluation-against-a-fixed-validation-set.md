# Automated evaluation against a fixed validation set

*How should models be validated before release?*

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images feed weekly retraining, and resulting models are pushed to production inspection devices.

## Decision Drivers

* Weekly retraining
* Production defect detection
* Small team

## Considered Options

* Automated evaluation against a fixed validation set
* Manual review of each candidate model

## Decision Outcome

Chosen option: "Automated evaluation against a fixed validation set".

A repeatable automated check better fits weekly retraining and a small team; the brief gives no basis for prescribing specific thresholds.

### Consequences

* The validation set and release criteria need ownership.
* Candidate models that pass may still fail on new production conditions.

## Pros and Cons of the Options

### Automated evaluation against a fixed validation set

* Good, because Repeatable release check
* Good, because Low manual effort
* Bad, because Validation set can become stale
* Bad, because Metrics may miss line-specific issues

### Manual review of each candidate model

* Good, because Human judgment of examples
* Good, because Can spot unusual failures
* Bad, because Slower weekly cadence
* Bad, because Review effort grows
