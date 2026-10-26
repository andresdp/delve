# How should production quality drift be detected?

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility when classification quality drifts. The design space’s monitoring dimension has low exclusivity, so monitoring practices can be combined; this ADR chooses drift monitoring as the primary practice.

## Decision Drivers

* Quality drift visibility
* Daily volume
* Seasonal demand swings

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Passive production operation (`v:6.4`)
* Periodic model health checks (`v:6.18`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Quality drift visibility decides the choice: “MLOps Principles” and “Machine Learning Monitoring: What It Is, and What We Are Missing” support watching input changes, while the checked point had no warnings but was unattested. Add prediction-quality measurement when labels become available; the design space treats monitoring as combinable, but the point tool warns when multiple monitoring values are checked together.

### Consequences

* Drift alerts require investigation and do not alone prove quality loss.
* Label availability and delay determine when prediction quality can be measured.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Quality drift: surfaces input and distribution changes
* Good, because Daily volume: monitors data without manual review of every item
* Bad, because Quality drift: drift is an indirect signal of prediction quality
* Sources: `s04_p03`, `s04_p05`, `s04_p12`, `s06_p02`, `s06_p08`, `s20_p03`, `s21_p10`, `s22_p11`, `s23_p03`, `s23_p04`, `s23_p05`, `s24_p01`, `s24_p07`, `s24_p08`, `s24_p11`, `s25_p01`

### Passive production operation

* Good, because Daily volume: minimal monitoring overhead
* Bad, because Quality drift: provides no active visibility
* Sources: `s13_p10`, `s21_p07`, `s23_p13`

### Periodic model health checks

* Good, because Cost: limits continuous monitoring work
* Bad, because Quality drift: issues may go unseen between checks
* Sources: `s06_p02`, `s20_p03`, `s21_p07`, `s23_p08`, `s23_p11`, `s24_p07`, `s24_p11`
