# Track labeled evaluation metrics over time

*How should classification quality drift be monitored?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. That requires quality signals over time and a way to surface changes to operators.

## Decision Drivers

* Quality drift visibility
* Operator needs
* LLM classifier

## Considered Options

* Track labeled evaluation metrics over time
* Monitor prediction and input statistics

## Decision Outcome

Chosen option: "Track labeled evaluation metrics over time".

Labeled evaluation metrics directly reflect classification quality, which is the drift operators need to observe.

### Consequences

* A labeled evaluation source is required.
* Metric thresholds and operator alerts must be defined.

## Pros and Cons of the Options

### Track labeled evaluation metrics over time

* Good, because Measures classification quality
* Good, because Supports trend detection
* Bad, because Needs labeled examples
* Bad, because Labels may arrive late

### Monitor prediction and input statistics

* Good, because Signals available quickly
* Good, because No labels required
* Bad, because Indirect quality evidence
* Bad, because May miss silent errors
