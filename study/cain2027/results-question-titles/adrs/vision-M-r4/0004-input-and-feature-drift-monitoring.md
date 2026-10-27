# Input and feature-drift monitoring

*How should production behavior be monitored?*

* System: On-device visual inspection

## Context and Problem Statement

Models run on disconnected devices, so quality and input changes may not be visible centrally in real time. The workspace supports combining monitoring practices because this dimension’s alternatives are not strongly exclusive.

## Decision Drivers

* Offline devices
* Defect quality
* Small team

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Schedule-based retraining trigger (`v:6.6`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Monitor input and feature distributions on-device and upload summaries when connectivity returns; combine that with the brief’s weekly retraining schedule. This gives the small team a signal for investigation without assuming always-on connectivity.

### Consequences

* Buffer monitoring summaries offline.
* Define drift thresholds and review steps.
* Schedule retraining weekly.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Flags changing inputs
* Good, because Supports investigation
* Bad, because Requires baseline data
* Bad, because May need delayed upload
* Sources: `s04_p03`, `s04_p05`, `s04_p12`, `s06_p02`, `s06_p08`, `s20_p03`, `s21_p10`, `s22_p11`, `s23_p03`, `s23_p04`, `s23_p05`, `s24_p01`, `s24_p07`, `s24_p08`, `s24_p11`, `s25_p01`

### Schedule-based retraining trigger

* Good, because Fits weekly cadence
* Good, because Simple trigger
* Bad, because Misses sudden drift
* Bad, because Does not prove quality
* Sources: `s06_p07`, `s06_p11`, `s20_p06`, `s20_p12`, `s22_p08`, `s24_p07`

### Passive production operation

* Good, because Little monitoring infrastructure
* Good, because Low operating effort
* Bad, because Failures may go unseen
* Bad, because No quality feedback
