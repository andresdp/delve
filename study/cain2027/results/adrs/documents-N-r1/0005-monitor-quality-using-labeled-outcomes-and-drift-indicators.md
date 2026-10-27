# Monitor quality using labeled outcomes and drift indicators

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts, but production predictions alone do not establish correctness. Quality monitoring needs outcome labels when available, alongside changes in prediction patterns.

## Decision Drivers

* Quality drift
* Operator visibility

## Considered Options

* Labeled outcome monitoring with drift indicators
* Prediction-volume monitoring only

## Decision Outcome

Chosen option: "Labeled outcome monitoring with drift indicators".

Outcome labels provide a quality signal, while prediction-pattern indicators can alert operators before enough labels accumulate.

### Consequences

* Define how labels are collected and joined to predictions.
* Tune alerts to limit noise.

## Pros and Cons of the Options

### Labeled outcome monitoring with drift indicators

* Good, because Measures observed quality
* Good, because Can surface shifts early
* Bad, because Labels may arrive late
* Bad, because Requires alert thresholds

### Prediction-volume monitoring only

* Good, because Available immediately
* Bad, because Does not measure correctness
* Bad, because May miss quality loss
