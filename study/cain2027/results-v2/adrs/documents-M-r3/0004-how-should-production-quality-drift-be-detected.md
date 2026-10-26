# How should production quality drift be detected?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space’s monitoring dimension has low exclusivity, so quality and input-drift monitoring can be combined.

## Decision Drivers

* Quality drift visibility
* Millions of documents daily

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Software-metrics-only monitoring (`v:6.10`)

## Decision Outcome

Chosen option: "Combined input-drift and prediction-quality monitoring".

The brief explicitly needs visibility into quality drift, so combine input and feature-drift monitoring with prediction-quality measurement when labels become available. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Machine Learning Monitoring: What It Is, and What We Are Missing” support these practices; this costs additional effort to collect labels and evaluate quality.

### Consequences

* Track input and feature distributions alongside quality metrics.
* Quality measurement depends on labeled outcomes becoming available.
* Set alert thresholds and ownership for investigation.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Drift visibility: detects changing inputs and features
* Good, because Volume: supports ongoing automated checks
* Bad, because Quality: input shifts do not prove accuracy loss
* Sources: `s04_p03`, `s04_p05`, `s04_p12`, `s06_p02`, `s06_p08`, `s20_p03`, `s21_p10`, `s22_p11`, `s23_p03`, `s23_p04`, `s23_p05`, `s24_p01`, `s24_p07`, `s24_p08`, `s24_p11`, `s25_p01`

### Real-time prediction-quality monitoring

* Good, because Quality: measures model behavior when labels arrive
* Good, because Drift visibility: reveals predictive degradation
* Bad, because Volume: depends on collecting and evaluating labels
* Sources: `s01_p06`, `s04_p02`, `s04_p12`, `s06_p06`, `s06_p13`, `s08_p02`, `s13_p10`, `s18_p01`, `s20_p02`, `s20_p03`, `s22_p11`, `s23_p03`, `s23_p04`, `s23_p05`, `s23_p08`, `s23_p11`, `s24_p01`, `s24_p05`, `s24_p07`, `s24_p08`, `s24_p11`

### Software-metrics-only monitoring

* Good, because Volume: tracks operational metrics at scale
* Bad, because Quality: misses model-specific drift signals
* Sources: `s20_p10`, `s23_p06`, `s23_p07`, `s23_p13`
