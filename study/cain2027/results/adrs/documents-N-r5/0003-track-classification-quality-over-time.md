# Track classification quality over time

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The system therefore needs quality measurements over time, not just per-request outputs.

## Decision Drivers

* Quality drift
* Operator visibility

## Considered Options

* Monitor operational metrics only
* Compare predictions with labeled outcomes

## Decision Outcome

Chosen option: "Compare predictions with labeled outcomes".

Comparing predictions with labeled outcomes directly measures quality, which is the drift operators need to detect.

### Consequences

* A source of labeled outcomes is required.
* Quality reports lag the arrival of labels.

## Pros and Cons of the Options

### Monitor operational metrics only

* Good, because Low data requirements
* Good, because Shows service health
* Bad, because Does not measure accuracy
* Bad, because Can miss quality drift

### Compare predictions with labeled outcomes

* Good, because Measures classification quality
* Good, because Can reveal drift
* Bad, because Needs labeled outcomes
* Bad, because Quality signals may arrive late
